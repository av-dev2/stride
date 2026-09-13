# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

"""Whitelisted GPS endpoints: on-demand provider queries and push ingestion."""

import frappe
from frappe import _

from stride.gps.sync import (
	create_gps_alarm,
	create_gps_log,
	sync_tracker_alarms,
	to_system_datetime,
	to_unix_seconds,
)


def get_tracker(tracker: str) -> "frappe.Document":
	"""Return a tracker the current user may read, or raise."""
	frappe.has_permission("GPS Tracker", "read", doc=tracker, throw=True)
	return frappe.get_doc("GPS Tracker", tracker)


# --------------------------------------------------------------------------
# On-demand provider queries
# --------------------------------------------------------------------------


@frappe.whitelist()
def get_device_detail(tracker: str) -> dict:
	"""Return device, account and bound-vehicle details straight from the provider."""
	doc = get_tracker(tracker)

	return doc.get_client().get_device_detail(doc.imei)


@frappe.whitelist()
def get_device_status(tracker: str) -> dict:
	"""Return the live status of one device: position, speed, heading, ignition and battery."""
	doc = get_tracker(tracker)

	devices = doc.get_client().get_device_status(imei=doc.imei)
	return devices[0] if devices else {}


@frappe.whitelist()
def get_live_location(tracker: str) -> dict:
	"""Return the reverse-geocoded live position of one device.

	The provider forbids polling this endpoint, so it is only reachable on user
	request and is never called by the scheduler.
	"""
	doc = get_tracker(tracker)

	return doc.get_client().get_device_location(doc.imei)


@frappe.whitelist()
def get_track_history(
	tracker: str, from_datetime: str, to_datetime: str, only_gps: bool = False
) -> list[dict]:
	"""Return the recorded trail of one device as map-ready points."""
	doc = get_tracker(tracker)

	points = doc.get_client().get_track_history(
		doc.imei,
		to_unix_seconds(from_datetime),
		to_unix_seconds(to_datetime),
		only_gps=only_gps,
	)

	return [
		{
			"timestamp": to_system_datetime(point.get("gpsTime")),
			"latitude": frappe.utils.flt(point.get("lat")),
			"longitude": frappe.utils.flt(point.get("lng")),
			"speed": frappe.utils.flt(point.get("speed")),
			"heading": frappe.utils.flt(point.get("course")),
			"position_type": point.get("positionType") or "",
			"acc_status": 1 if point.get("accStatus") else 0,
		}
		for point in points
	]


@frappe.whitelist()
def get_mileage(tracker: str, from_datetime: str, to_datetime: str) -> dict:
	"""Return distance travelled and running time for one device over a period."""
	doc = get_tracker(tracker)

	return doc.get_client().get_mileage(
		doc.imei, to_unix_seconds(from_datetime), to_unix_seconds(to_datetime)
	)


@frappe.whitelist()
def get_locations_by_user(
	provider: str, account_id: str | None = None, include_sub: bool = True
) -> list[dict]:
	"""Return bare device positions for an account, used to reconcile unregistered devices."""
	frappe.has_permission("GPS Provider", "read", doc=provider, throw=True)
	doc = frappe.get_doc("GPS Provider", provider)

	return doc.get_client().get_locations_by_organization(
		account_id or doc.account_id, include_sub=include_sub
	)


@frappe.whitelist()
def get_vehicle_locations(provider: str, account_id: str | None = None) -> dict:
	"""Return provider-side vehicle positions keyed by number plate (Vehicle Location 2.0)."""
	frappe.has_permission("GPS Provider", "read", doc=provider, throw=True)
	doc = frappe.get_doc("GPS Provider", provider)

	return doc.get_client().get_vehicle_locations(account_id or doc.account_id)


@frappe.whitelist()
def get_vehicle_status(vehicle: str, provider: str | None = None) -> list[dict]:
	"""Return provider-side device status for a vehicle, looked up by its number plate."""
	frappe.has_permission("Vehicle", "read", doc=vehicle, throw=True)

	license_plate = frappe.db.get_value("Vehicle", vehicle, "license_plate") or vehicle
	provider = provider or frappe.db.get_value(
		"GPS Tracker", {"vehicle": vehicle, "is_active": 1}, "gps_provider", order_by="creation asc"
	)

	if not provider:
		frappe.throw(_("No GPS Provider is configured for Vehicle {0}.").format(vehicle))

	return frappe.get_doc("GPS Provider", provider).get_client().get_vehicle_status(license_plate)


# --------------------------------------------------------------------------
# Ingestion
# --------------------------------------------------------------------------


@frappe.whitelist(methods=["POST"])
def pull_alarms(tracker: str, from_datetime: str, to_datetime: str) -> dict:
	"""Fetch alarm records for a tracker and store the new ones as GPS Alarms."""
	frappe.has_permission("GPS Alarm", "create", throw=True)
	get_tracker(tracker)

	return sync_tracker_alarms(tracker, from_datetime, to_datetime)


@frappe.whitelist(methods=["POST"])
def poll_now(provider: str) -> dict:
	"""Refresh positions for one provider immediately, ignoring its polling interval."""
	frappe.only_for("System Manager")

	from stride.gps.sync import sync_provider_positions

	return sync_provider_positions(provider)


@frappe.whitelist(methods=["POST"])
def receive_gps_data(
	imei: str,
	timestamp: int | None = None,
	latitude: float | None = None,
	longitude: float | None = None,
	speed: float | None = None,
	heading: float | None = None,
	address: str | None = None,
	device_status: str | None = None,
	acc_status: bool | None = None,
	alarm_code: str | None = None,
	alarm_message: str | None = None,
) -> dict:
	"""Accept one position push from a tracking device.

	Endpoint: POST /api/method/stride.api.gps.receive_gps_data

	Timestamps are unix seconds, matching the provider convention. An alarm_code
	turns the payload into a GPS Alarm as well as a position sample.
	"""
	frappe.has_permission("GPS Log", "create", throw=True)

	return store_pushed_point(
		_resolve_tracker(imei),
		{
			"timestamp": timestamp,
			"latitude": latitude,
			"longitude": longitude,
			"speed": speed,
			"heading": heading,
			"address": address,
			"device_status": device_status,
			"acc_status": acc_status,
			"alarm_code": alarm_code,
			"alarm_message": alarm_message,
		},
	)


def store_pushed_point(tracker: frappe._dict, point: dict) -> dict:
	"""Store one pushed reading as a GPS Log, and as a GPS Alarm when it carries a code."""
	timestamp = point.get("timestamp")
	latitude = point.get("latitude")
	longitude = point.get("longitude")
	speed = point.get("speed")
	heading = point.get("heading")
	address = point.get("address")
	alarm_code = point.get("alarm_code")

	payload = {
		"gpsTime": timestamp,
		"lat": latitude,
		"lng": longitude,
		"speed": speed,
		"course": heading,
		"address": address,
		"status": point.get("device_status"),
		"accStatus": point.get("acc_status"),
	}

	created_log = create_gps_log(tracker, payload)
	created_alarm = False

	if alarm_code:
		created_alarm = create_gps_alarm(
			tracker,
			{
				"alarmCode": alarm_code,
				"alarmTime": timestamp,
				"message": point.get("alarm_message"),
				"lat": latitude,
				"lng": longitude,
				"speed": speed,
				"course": heading,
				"address": address,
			},
		)

	return {"gps_log": created_log, "gps_alarm": created_alarm}


@frappe.whitelist(methods=["POST"])
def receive_gps_batch(data: list) -> dict:
	"""Accept a batch of position pushes, one dict per point.

	Endpoint: POST /api/method/stride.api.gps.receive_gps_batch

	Each dict takes the same keys as receive_gps_data. Points that fail are
	reported by index rather than failing the whole batch.
	"""
	frappe.has_permission("GPS Log", "create", throw=True)
	data = frappe.parse_json(data) if isinstance(data, str) else data

	# A batch from one device repeats the same IMEI, so resolve each one once.
	trackers = {}
	created = 0
	errors = []

	for index, point in enumerate(data):
		try:
			imei = point["imei"]
			if imei not in trackers:
				trackers[imei] = _resolve_tracker(imei)

			if store_pushed_point(trackers[imei], point)["gps_log"]:
				created += 1
		except Exception as error:
			errors.append({"index": index, "error": str(error)})

	return {"created": created, "errors": errors}


def _resolve_tracker(imei: str) -> frappe._dict:
	"""Return the vehicle-bound tracker for an IMEI, or raise."""
	tracker = frappe.db.get_value("GPS Tracker", {"imei": imei}, ["name", "vehicle"], as_dict=True)

	if not tracker:
		frappe.throw(_("No GPS Tracker is registered for IMEI {0}.").format(imei))

	if not tracker.vehicle:
		frappe.throw(_("GPS Tracker {0} is not linked to a Vehicle.").format(tracker.name))

	return tracker
