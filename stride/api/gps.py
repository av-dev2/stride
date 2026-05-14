# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

"""GPS API endpoint for receiving data from IOPGPS tracking platform."""

import frappe
from frappe import _


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
