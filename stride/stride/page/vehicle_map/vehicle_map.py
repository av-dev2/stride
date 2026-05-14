# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

"""Server-side methods for the Vehicle Map page."""

import frappe


@frappe.whitelist()
def get_vehicle_locations() -> list[dict]:
	"""Return the latest GPS location for each vehicle.

	For each vehicle that has a GPS Log, returns the most recent
	record with coordinates, speed, heading, and alert info.
	"""
	# Get distinct vehicles with GPS data
	vehicles = frappe.db.get_all(
		"GPS Log",
		fields=["vehicle"],
		group_by="vehicle",
		pluck="vehicle",
	)

	if not vehicles:
		return []

	locations = []

	for vehicle_name in vehicles:
		# Get the latest GPS log for this vehicle
		latest_log = frappe.db.get_value(
			"GPS Log",
			filters={"vehicle": vehicle_name},
			fieldname=[
				"name",
				"vehicle",
				"timestamp",
				"latitude",
				"longitude",
				"speed",
				"heading",
				"address",
				"alert_type",
				"alert_message",
			],
			order_by="timestamp desc",
			as_dict=True,
		)

		if latest_log and latest_log.latitude and latest_log.longitude:
			# Get vehicle details
			vehicle_info = frappe.db.get_value(
				"Vehicle",
				vehicle_name,
				["license_plate", "make", "model", "vehicle_value"],
				as_dict=True,
			)

			latest_log.update(
				{
					"license_plate": vehicle_info.license_plate if vehicle_info else vehicle_name,
					"make": vehicle_info.make if vehicle_info else "",
					"model": vehicle_info.model if vehicle_info else "",
				}
			)
			locations.append(latest_log)

	return locations


@frappe.whitelist()
def get_vehicle_route(vehicle: str, from_date: str, to_date: str) -> list[dict]:
	"""Return GPS logs for a vehicle in a date range (route history).

	Args:
	        vehicle: Vehicle name.
	        from_date: Start date (YYYY-MM-DD).
	        to_date: End date (YYYY-MM-DD).

	Returns:
	        List of GPS Log dicts ordered by timestamp.
	"""
	return frappe.db.get_all(
		"GPS Log",
		filters={
			"vehicle": vehicle,
			"timestamp": ("between", [from_date, to_date]),
		},
		fields=[
			"timestamp",
			"latitude",
			"longitude",
			"speed",
			"heading",
			"address",
			"alert_type",
			"alert_message",
		],
		order_by="timestamp asc",
		limit_page_length=5000,
	)
