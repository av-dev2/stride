# Copyright (c) 2026, elius-dev and contributors
# For license information, please see license.txt

"""Ingestion of GPS provider payloads into GPS Log and GPS Alarm records."""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import frappe
from frappe.utils import (
	add_to_date,
	convert_utc_to_system_timezone,
	flt,
	get_datetime,
	get_system_timezone,
	now_datetime,
)


def to_system_datetime(unix_seconds) -> str | None:
	"""Convert an IOPGPS unix-second timestamp into a site-timezone datetime string."""
	if not unix_seconds:
		return None

	utc_time = datetime.fromtimestamp(int(unix_seconds), tz=UTC)
	return convert_utc_to_system_timezone(utc_time).strftime("%Y-%m-%d %H:%M:%S")


def to_unix_seconds(value) -> int:
	"""Convert a datetime or datetime string into unix seconds for IOPGPS query parameters."""
	local_time = get_datetime(value).replace(tzinfo=ZoneInfo(get_system_timezone()))
	return int(local_time.timestamp())


def get_active_trackers(provider: str) -> dict[str, frappe._dict]:
	"""Return active, vehicle-bound trackers of a provider, keyed by IMEI."""
	trackers = frappe.get_all(
		"GPS Tracker",
		filters={"gps_provider": provider, "is_active": 1, "vehicle": ("is", "set")},
		fields=["name", "imei", "vehicle"],
	)
	return {tracker.imei: tracker for tracker in trackers}


def sync_provider_positions(provider_name: str) -> dict:
	"""Fetch every device status on a provider account and store new position samples.

	One request covers the whole account, which keeps the job inside the provider
	rate limits regardless of fleet size.
	"""
	provider = frappe.get_doc("GPS Provider", provider_name)
	trackers = get_active_trackers(provider.name)

	if not trackers:
		return {"created": 0, "skipped": 0}

	devices = provider.get_client().get_device_status()

	created = 0
	skipped = 0

	for device in devices:
		tracker = trackers.get(str(device.get("imei") or ""))
		if not tracker:
			skipped += 1
			continue

		if create_gps_log(tracker, device):
			created += 1
		else:
			skipped += 1

	provider.db_set("last_polled_on", now_datetime(), update_modified=False)

	return {"created": created, "skipped": skipped}


def create_gps_log(tracker: frappe._dict, device: dict) -> bool:
	"""Store one device status payload as a GPS Log. Returns False when it is not usable or a duplicate."""
	timestamp = to_system_datetime(device.get("gpsTime") or device.get("signalTime"))
	latitude = flt(device.get("lat"))
	longitude = flt(device.get("lng"))

	# A device with no fix reports 0,0, which is a position off the coast of Africa.
	if not timestamp or not latitude or not longitude:
		return False

	log = frappe.get_doc(
		{
			"doctype": "GPS Log",
			"vehicle": tracker.vehicle,
			"gps_tracker": tracker.name,
			"timestamp": timestamp,
			"latitude": latitude,
			"longitude": longitude,
			"speed": flt(device.get("speed")),
			"heading": flt(device.get("course")),
			"address": device.get("address") or "",
			"device_status": device.get("status") or "",
			"acc_status": 1 if device.get("accStatus") else 0,
			"position_type": device.get("positionType") or "",
			"battery_percentage": flt(device.get("chargePercentage")),
		}
	)

	if not insert_unless_duplicate(log):
		return False

	update_tracker_state(tracker.name, device, timestamp)
	return True


def update_tracker_state(tracker_name: str, device: dict, timestamp: str) -> None:
	"""Cache the last reported status on the tracker so the list view stays useful.

	Only fields the payload carries are written; a pushed position has no SIM
	number and must not blank the one already recorded.
	"""
	state = {"last_seen_on": timestamp}

	if device.get("status"):
		state["last_status"] = device["status"]
	if device.get("sim"):
		state["sim_number"] = device["sim"]

	frappe.db.set_value("GPS Tracker", tracker_name, state, update_modified=False)


def sync_tracker_alarms(tracker_name: str, from_datetime, to_datetime) -> dict:
	"""Pull alarm records for one tracker in a time range and store the new ones."""
	tracker = frappe.get_doc("GPS Tracker", tracker_name)

	if not tracker.vehicle:
		frappe.throw(frappe._("GPS Tracker {0} is not linked to a Vehicle.").format(tracker.name))

	provider = frappe.get_doc("GPS Provider", tracker.gps_provider)
	alarms = provider.get_client().get_alarms(
		tracker.imei, to_unix_seconds(from_datetime), to_unix_seconds(to_datetime)
	)

	created = sum(1 for alarm in alarms if create_gps_alarm(tracker, alarm))

	return {"created": created, "fetched": len(alarms)}


def create_gps_alarm(tracker, alarm: dict) -> bool:
	"""Store one alarm payload as a GPS Alarm. Returns False when it is a duplicate."""
	alarm_time = to_system_datetime(alarm.get("alarmTime") or alarm.get("time"))
	alarm_code = str(alarm.get("alarmCode") or "")

	if not alarm_time or not alarm_code:
		return False

	media = alarm.get("extData") or {}

	alarm_doc = frappe.get_doc(
		{
			"doctype": "GPS Alarm",
			"vehicle": tracker.vehicle,
			"gps_tracker": tracker.name,
			"alarm_code": alarm_code,
			"alarm_description": alarm.get("message") or "",
			"alarm_time": alarm_time,
			"latitude": flt(alarm.get("lat")),
			"longitude": flt(alarm.get("lng")),
			"speed": flt(alarm.get("speed")),
			"heading": flt(alarm.get("course")),
			"address": alarm.get("address") or "",
			"position_type": alarm.get("positionType") or "",
			"battery_capacity": flt(alarm.get("batteryCapacity")),
			"video_url": media.get("mp4") or "",
			"archive_url": media.get("zip") or "",
			"image_urls": "\n".join(media.get("images") or []),
		}
	)

	return insert_unless_duplicate(alarm_doc)


def insert_unless_duplicate(doc) -> bool:
	"""Insert a reading, treating a duplicate as already stored rather than an error.

	The preceding existence check is not atomic, so two workers polling the same
	provider can both reach the insert. A unique constraint decides the winner.
	"""
	try:
		doc.insert(ignore_permissions=True)
	except (frappe.DuplicateEntryError, frappe.UniqueValidationError):
		return False

	return True


def poll_due_providers() -> None:
	"""Refresh positions for every enabled provider whose polling interval has elapsed."""
	for provider in frappe.get_all(
		"GPS Provider",
		filters={"enabled": 1},
		fields=["name", "polling_interval_minutes", "last_polled_on"],
	):
		if not is_polling_due(provider):
			continue

		try:
			sync_provider_positions(provider.name)
		except Exception:
			frappe.log_error(
				title=f"GPS polling failed: {provider.name}",
				message=frappe.get_traceback(),
			)


def is_polling_due(provider: frappe._dict) -> bool:
	"""True when the provider has never been polled or its interval has elapsed."""
	if not provider.last_polled_on:
		return True

	interval = provider.polling_interval_minutes or 15
	return add_to_date(provider.last_polled_on, minutes=interval) <= now_datetime()


def refresh_expiring_tokens() -> None:
	"""Renew access tokens that are close to expiry, so requests rarely pay the handshake."""
	for name in frappe.get_all("GPS Provider", filters={"enabled": 1}, pluck="name"):
		provider = frappe.get_doc("GPS Provider", name)

		if provider.has_valid_token:
			continue

		try:
			provider.refresh_access_token()
		except Exception:
			frappe.log_error(
				title=f"GPS token refresh failed: {name}",
				message=frappe.get_traceback(),
			)
