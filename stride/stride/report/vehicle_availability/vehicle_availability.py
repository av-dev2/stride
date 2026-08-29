# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

"""Vehicle Availability Report.

Fleet overview showing each vehicle's status, current lease info,
and GPS tracking status.
"""

import frappe
from frappe import _


def execute(filters: dict | None = None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart


def get_columns() -> list[dict]:
	return [
		{
			"label": _("Vehicle"),
			"fieldname": "vehicle",
			"fieldtype": "Link",
			"options": "Vehicle",
			"width": 140,
		},
		{
			"label": _("License Plate"),
			"fieldname": "license_plate",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Make"),
			"fieldname": "make",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Model"),
			"fieldname": "model",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Status"),
			"fieldname": "vehicle_status",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Current Customer"),
			"fieldname": "current_customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 140,
		},
		{
			"label": _("Current Lease"),
			"fieldname": "current_lease",
			"fieldtype": "Link",
			"options": "Lease",
			"width": 140,
		},
		{
			"label": _("Lease End Date"),
			"fieldname": "lease_end_date",
			"fieldtype": "Date",
			"width": 110,
		},
		{
			"label": _("GPS Tracker"),
			"fieldname": "gps_tracker_id",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Vehicle Value"),
			"fieldname": "vehicle_value",
			"fieldtype": "Currency",
			"width": 130,
		},
	]


def get_data(filters: dict | None = None) -> list[dict]:
	v_filters: dict = {}
	if filters:
		if filters.get("vehicle_status"):
			v_filters["vehicle_status"] = filters["vehicle_status"]
		if filters.get("make"):
			v_filters["make"] = filters["make"]

	vehicles = frappe.db.get_all(
		"Vehicle",
		filters=v_filters,
		fields=[
			"name",
			"license_plate",
			"make",
			"model",
			"vehicle_status",
			"gps_tracker_id",
			"vehicle_value",
		],
		order_by="name asc",
	)

	data = []
	for v in vehicles:
		# Find the latest active (submitted) lease
		active_lease = frappe.db.get_value(
			"Lease",
			filters={
				"vehicle": v.name,
				"docstatus": 1,
				"status": ("in", ["Active", "Overdue"]),
			},
			fieldname=["name", "customer", "end_date"],
			order_by="creation desc",
			as_dict=True,
		)

		data.append(
			{
				"vehicle": v.name,
				"license_plate": v.license_plate,
				"make": v.make,
				"model": v.model,
				"vehicle_status": v.vehicle_status or "Available",
				"current_customer": active_lease.customer if active_lease else None,
				"current_lease": active_lease.name if active_lease else None,
				"lease_end_date": active_lease.end_date if active_lease else None,
				"gps_tracker_id": v.gps_tracker_id or "",
				"vehicle_value": v.vehicle_value,
			}
		)

	return data


def get_chart_data(data: list[dict]) -> dict:
	"""Return vehicle status distribution for pie chart."""
	status_counts: dict[str, int] = {}
	for row in data:
		status = row.get("vehicle_status") or "Unknown"
		status_counts[status] = status_counts.get(status, 0) + 1

	if not status_counts:
		return {}

	return {
		"data": {
			"labels": list(status_counts.keys()),
			"datasets": [{"values": list(status_counts.values())}],
		},
		"type": "donut",
		"height": 280,
	}
