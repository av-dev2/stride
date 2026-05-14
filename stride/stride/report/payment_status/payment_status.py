# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

"""Payment Status Report.

Shows all Lease Payment Schedule rows with filters for status,
vehicle, customer, and date range.
"""

import frappe
from frappe import _
from frappe.utils import getdate


def execute(filters: dict | None = None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns() -> list[dict]:
	return [
		{
			"label": _("Lease"),
			"fieldname": "lease",
			"fieldtype": "Link",
			"options": "Lease",
			"width": 140,
		},
		{
			"label": _("Vehicle"),
			"fieldname": "vehicle",
			"fieldtype": "Link",
			"options": "Vehicle",
			"width": 120,
		},
		{
			"label": _("License Plate"),
			"fieldname": "license_plate",
			"fieldtype": "Data",
			"width": 110,
		},
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 140,
		},
		{
			"label": _("Customer Name"),
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Period"),
			"fieldname": "period",
			"fieldtype": "Int",
			"width": 70,
		},
		{
			"label": _("From Date"),
			"fieldname": "from_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("To Date"),
			"fieldname": "to_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("Due Date"),
			"fieldname": "due_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 90,
		},
		{
			"label": _("Sales Invoice"),
			"fieldname": "sales_invoice",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 140,
		},
	]


def get_data(filters: dict | None = None) -> list[dict]:
	lease_filters = {"docstatus": 1}
	if filters:
		if filters.get("vehicle"):
			lease_filters["vehicle"] = filters["vehicle"]
		if filters.get("customer"):
			lease_filters["customer"] = filters["customer"]
		if filters.get("status") and filters["status"] != "All":
			lease_filters["status"] = filters["status"]

	leases = frappe.db.get_all(
		"Lease",
		filters=lease_filters,
		fields=["name", "vehicle", "customer", "customer_name"],
	)

	if not leases:
		return []

	data = []
	for lease in leases:
		# Get vehicle license plate
		license_plate = frappe.db.get_value("Vehicle", lease.vehicle, "license_plate") or ""

		schedule_filters = {"parent": lease.name}
		if filters and filters.get("payment_status"):
			schedule_filters["status"] = filters["payment_status"]

		rows = frappe.db.get_all(
			"Lease Payment Schedule",
			filters=schedule_filters,
			fields=[
				"period",
				"from_date",
				"to_date",
				"due_date",
				"amount",
				"status",
				"sales_invoice",
			],
			order_by="period asc",
		)

		for row in rows:
			# Apply date range filter if specified
			if filters:
				if filters.get("from_date") and getdate(row.due_date) < getdate(filters["from_date"]):
					continue
				if filters.get("to_date") and getdate(row.due_date) > getdate(filters["to_date"]):
					continue

			data.append(
				{
					"lease": lease.name,
					"vehicle": lease.vehicle,
					"license_plate": license_plate,
					"customer": lease.customer,
					"customer_name": lease.customer_name,
					"period": row.period,
					"from_date": row.from_date,
					"to_date": row.to_date,
					"due_date": row.due_date,
					"amount": row.amount,
					"status": row.status,
					"sales_invoice": row.sales_invoice,
				}
			)

	return data
