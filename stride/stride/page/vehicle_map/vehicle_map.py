# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

"""Server-side methods for the Vehicle Map page."""

import frappe
from frappe.query_builder.functions import Max
from frappe.utils import add_to_date, now_datetime

ALARM_WINDOW_HOURS = 24
ROUTE_POINT_LIMIT = 5000


@frappe.whitelist()
def get_vehicle_locations() -> list[dict]:
	"""Return the latest position of every tracked vehicle, with any recent alarm.

	The newest GPS Log per vehicle is selected in one query, joined to the Vehicle
	for display details, and annotated with alarms raised in the last day.
	"""
	frappe.has_permission("GPS Log", "read", throw=True)

	locations = _fetch_latest_positions()

	if not locations:
		return []

	alarms = _fetch_recent_alarms([row["vehicle"] for row in locations])

	for row in locations:
		alarm = alarms.get(row["vehicle"])
		row["alarm_code"] = alarm.alarm_code if alarm else None
		row["alarm_description"] = alarm.alarm_description if alarm else None
		row["alarm_time"] = alarm.alarm_time if alarm else None

	return locations


def _fetch_latest_positions() -> list[dict]:
	"""Return one row per vehicle holding its most recent GPS Log and vehicle details."""
	gps_log = frappe.qb.DocType("GPS Log")
	vehicle = frappe.qb.DocType("Vehicle")
	newest = frappe.qb.DocType("GPS Log").as_("newest")

	latest_per_vehicle = (
		frappe.qb.from_(newest)
		.select(newest.vehicle, Max(newest.timestamp).as_("timestamp"))
		.groupby(newest.vehicle)
	)

	rows = (
		frappe.qb.from_(gps_log)
		.inner_join(latest_per_vehicle)
		.on(
			(gps_log.vehicle == latest_per_vehicle.vehicle)
			& (gps_log.timestamp == latest_per_vehicle.timestamp)
		)
		.left_join(vehicle)
		.on(gps_log.vehicle == vehicle.name)
		.select(
			gps_log.name,
			gps_log.vehicle,
			gps_log.gps_tracker,
			gps_log.timestamp,
			gps_log.latitude,
			gps_log.longitude,
			gps_log.speed,
			gps_log.heading,
			gps_log.address,
			gps_log.device_status,
			gps_log.acc_status,
			gps_log.position_type,
			gps_log.battery_percentage,
			vehicle.license_plate,
			vehicle.make,
			vehicle.model,
		)
		.where((gps_log.latitude != 0) & (gps_log.longitude != 0))
		.run(as_dict=True)
	)

	# A vehicle may carry several trackers, and two of them reporting the same
	# second both satisfy the newest-timestamp join. The map draws one marker per
	# vehicle, so the extra rows would stack invisibly on top of each other.
	newest_per_vehicle = {}
	for row in rows:
		newest_per_vehicle.setdefault(row["vehicle"], row)

	return list(newest_per_vehicle.values())


def _fetch_recent_alarms(vehicles: list[str]) -> dict[str, frappe._dict]:
	"""Return the newest alarm of the last day per vehicle, keyed by vehicle."""
	since = add_to_date(now_datetime(), hours=-ALARM_WINDOW_HOURS)

	alarms = frappe.get_all(
		"GPS Alarm",
		filters={"vehicle": ("in", vehicles), "alarm_time": (">=", since)},
		fields=["vehicle", "alarm_code", "alarm_description", "alarm_time"],
		order_by="alarm_time asc",
	)

	# Later rows overwrite earlier ones, leaving the newest alarm per vehicle.
	return {alarm.vehicle: alarm for alarm in alarms}


@frappe.whitelist()
def get_vehicle_route(
	vehicle: str, from_date: str, to_date: str, gps_tracker: str | None = None
) -> list[dict]:
	"""Return stored GPS Logs for a vehicle in a date range, ordered oldest first."""
	frappe.has_permission("Vehicle", "read", doc=vehicle, throw=True)

	filters = {"vehicle": vehicle, "timestamp": ("between", [from_date, to_date])}
	if gps_tracker:
		filters["gps_tracker"] = gps_tracker

	return frappe.get_all(
		"GPS Log",
		filters=filters,
		fields=[
			"timestamp",
			"gps_tracker",
			"latitude",
			"longitude",
			"speed",
			"heading",
			"address",
			"device_status",
			"acc_status",
		],
		order_by="timestamp asc",
		limit=ROUTE_POINT_LIMIT,
	)


@frappe.whitelist()
def get_vehicle_alarms(vehicle: str, from_date: str, to_date: str) -> list[dict]:
	"""Return stored alarms for a vehicle in a date range, newest first."""
	frappe.has_permission("Vehicle", "read", doc=vehicle, throw=True)

	return frappe.get_all(
		"GPS Alarm",
		filters={"vehicle": vehicle, "alarm_time": ("between", [from_date, to_date])},
		fields=[
			"name",
			"gps_tracker",
			"alarm_code",
			"alarm_description",
			"alarm_time",
			"latitude",
			"longitude",
			"speed",
			"address",
			"video_url",
			"image_urls",
		],
		order_by="alarm_time desc",
		limit=ROUTE_POINT_LIMIT,
	)
