# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

"""GPS API endpoint for receiving data from IOPGPS tracking platform."""

import frappe
import requests
from frappe import _
from frappe.utils import now_datetime

# --------------------------------------------------------------------------
# IOPGPS Polling Integration (Task 18)
# --------------------------------------------------------------------------

IOPGPS_TOKEN_CACHE_KEY = "iopgps_access_token"
IOPGPS_TOKEN_TTL = 90 * 60  # 90 minutes (token valid for 2h, refresh early)


def _get_iopgps_token(settings: "frappe._dict") -> str:
	"""Get a valid IOPGPS access_token, using cache when available.

	The token is cached in Redis for 90 minutes (IOPGPS tokens expire after 2h).
	"""
	cached = frappe.cache.get_value(IOPGPS_TOKEN_CACHE_KEY)
	if cached:
		return cached

	api_url = settings.gps_api_url.rstrip("/")
	api_key = settings.get_password("gps_api_key")

	if not api_key:
		frappe.throw(_("GPS API Key is not configured in Stride Settings."))

	# IOPGPS authentication endpoint
	auth_url = f"{api_url}/api/auth/login"
	resp = requests.post(
		auth_url,
		json={"account": settings.gps_account or "", "password": api_key},
		timeout=30,
	)
	resp.raise_for_status()

	data = resp.json()
	token = data.get("access_token") or data.get("token") or data.get("data", {}).get("access_token")

	if not token:
		frappe.throw(_("Failed to obtain IOPGPS access token. Response: {0}").format(str(data)))

	frappe.cache.set_value(IOPGPS_TOKEN_CACHE_KEY, token, expires_in_sec=IOPGPS_TOKEN_TTL)
	return token


def _fetch_device_locations(api_url: str, token: str) -> list[dict]:
	"""Fetch real-time locations for all devices from IOPGPS API."""
	url = f"{api_url.rstrip('/')}/api/device/location"
	resp = requests.get(
		url,
		params={"access_token": token},
		timeout=30,
	)
	resp.raise_for_status()

	data = resp.json()
	# IOPGPS may return data under "data", "list", or at top level
	if isinstance(data, list):
		return data
	if isinstance(data, dict):
		return data.get("data") or data.get("list") or []
	return []


def poll_iopgps_locations() -> dict:
	"""Poll IOPGPS API for all device locations and create GPS Log records.

	Called by the scheduled cron job (every N minutes).
	Matches IOPGPS devices to Vehicles via the `gps_tracker_id` custom field.

	Returns:
	    dict with created count and errors
	"""
	settings = frappe.get_cached_doc("Stride Settings")

	if not settings.gps_api_url:
		frappe.log_error(
			title=_("GPS Polling: Missing API URL"),
			message=_("Please configure the GPS API URL in Stride Settings."),
		)
		return {"created": 0, "errors": ["Missing GPS API URL"]}

	# Build a mapping of tracker_id → vehicle_name for fast lookup
	tracker_map = _build_tracker_map()

	if not tracker_map:
		frappe.logger("stride").info("GPS Polling: No vehicles with gps_tracker_id configured.")
		return {"created": 0, "errors": []}

	try:
		token = _get_iopgps_token(settings)
		devices = _fetch_device_locations(settings.gps_api_url, token)
	except Exception:
		frappe.log_error(
			title=_("GPS Polling: API Error"),
			message=frappe.get_traceback(),
		)
		return {"created": 0, "errors": ["API request failed"]}

	created = 0
	errors = []

	for device in devices:
		try:
			created += _process_device_location(device, tracker_map)
		except Exception as e:
			errors.append(str(e))

	if created:
		frappe.logger("stride").info(f"GPS Polling: {created} GPS Log records created.")

	return {"created": created, "errors": errors}


def _build_tracker_map() -> dict[str, str]:
	"""Build a mapping of gps_tracker_id → vehicle name."""
	vehicles = frappe.db.get_all(
		"Vehicle",
		filters={"gps_tracker_id": ("is", "set")},
		fields=["name", "gps_tracker_id"],
	)
	return {v.gps_tracker_id: v.name for v in vehicles}


def _process_device_location(device: dict, tracker_map: dict) -> int:
	"""Process a single device location record from IOPGPS.

	Args:
	    device: Raw device dict from IOPGPS API
	    tracker_map: gps_tracker_id → vehicle_name mapping

	Returns:
	    1 if a GPS Log was created, 0 otherwise
	"""
	# IOPGPS may use imei, deviceId, or id as the device identifier
	device_id = str(device.get("imei") or device.get("deviceId") or device.get("id") or "")
	if not device_id or device_id not in tracker_map:
		return 0

	vehicle_name = tracker_map[device_id]

	lat = device.get("lat") or device.get("latitude")
	lng = device.get("lng") or device.get("longitude")

	if not lat or not lng:
		return 0

	# Parse timestamp — IOPGPS may return seconds or ISO string
	raw_ts = device.get("gpsTime") or device.get("timestamp") or device.get("positionTime")
	if isinstance(raw_ts, int | float):
		from datetime import datetime

		timestamp = datetime.fromtimestamp(raw_ts).strftime("%Y-%m-%d %H:%M:%S")
	elif raw_ts:
		timestamp = str(raw_ts)
	else:
		timestamp = now_datetime()

	# Dedup: skip if we already have a GPS Log for this vehicle+timestamp
	if frappe.db.exists("GPS Log", {"vehicle": vehicle_name, "timestamp": timestamp}):
		return 0

	gps_log = frappe.new_doc("GPS Log")
	gps_log.update(
		{
			"vehicle": vehicle_name,
			"timestamp": timestamp,
			"latitude": float(lat),
			"longitude": float(lng),
			"speed": float(device.get("speed") or 0),
			"heading": float(device.get("course") or device.get("heading") or 0),
			"address": device.get("address") or "",
			"alert_type": device.get("alarmType") or device.get("alert_type") or "",
			"alert_message": device.get("alarmData") or device.get("alert_message") or "",
		}
	)
	gps_log.insert(ignore_permissions=True)
	return 1


@frappe.whitelist(methods=["POST"])
def receive_gps_data(
	vehicle: str,
	timestamp: str,
	latitude: float | None = None,
	longitude: float | None = None,
	speed: float | None = None,
	heading: float | None = None,
	address: str | None = None,
	alert_type: str | None = None,
	alert_message: str | None = None,
) -> dict:
	"""Receive GPS data from IOPGPS and create a GPS Log record.

	Endpoint: POST /api/method/stride.api.gps.receive_gps_data

	Args:
	        vehicle: Vehicle name (license plate)
	        timestamp: ISO datetime string
	        latitude: GPS latitude coordinate
	        longitude: GPS longitude coordinate
	        speed: Vehicle speed in km/h
	        heading: Compass heading in degrees
	        address: Reverse-geocoded address
	        alert_type: IOPGPS alert type (e.g. "overspeed", "geofence")
	        alert_message: Alert details

	Returns:
	        dict with created GPS Log name
	"""
	if not frappe.db.exists("Vehicle", vehicle):
		frappe.throw(_("Vehicle {0} not found.").format(vehicle))

	gps_log = frappe.new_doc("GPS Log")
	gps_log.vehicle = vehicle
	gps_log.timestamp = timestamp
	gps_log.latitude = latitude
	gps_log.longitude = longitude
	gps_log.speed = speed
	gps_log.heading = heading
	gps_log.address = address
	gps_log.alert_type = alert_type
	gps_log.alert_message = alert_message
	gps_log.insert(ignore_permissions=True)

	return {"gps_log": gps_log.name, "status": "ok"}


@frappe.whitelist(methods=["POST"])
def receive_gps_batch(data: list) -> dict:
	"""Receive a batch of GPS data points.

	Endpoint: POST /api/method/stride.api.gps.receive_gps_batch

	Args:
	        data: List of dicts, each with the same fields as receive_gps_data

	Returns:
	        dict with count of created records and any errors
	"""
	created = 0
	errors = []

	for idx, point in enumerate(data):
		try:
			vehicle = point.get("vehicle")
			if not vehicle or not frappe.db.exists("Vehicle", vehicle):
				errors.append({"index": idx, "error": f"Vehicle not found: {vehicle}"})
				continue

			gps_log = frappe.new_doc("GPS Log")
			gps_log.update(
				{
					"vehicle": vehicle,
					"timestamp": point.get("timestamp"),
					"latitude": point.get("latitude"),
					"longitude": point.get("longitude"),
					"speed": point.get("speed"),
					"heading": point.get("heading"),
					"address": point.get("address"),
					"alert_type": point.get("alert_type"),
					"alert_message": point.get("alert_message"),
				}
			)
			gps_log.insert(ignore_permissions=True)
			created += 1
		except Exception as e:
			errors.append({"index": idx, "error": str(e)})

	return {"created": created, "errors": errors}
