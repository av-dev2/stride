# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

"""Contract Summary Report.

Shows active, completed, and cancelled contracts with
customer, vehicle, financials, and status breakdown.
"""

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters: dict | None = None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    return columns, data, None, chart


def get_columns() -> list[dict]:
    return [
        {
            "label": _("Contract"),
            "fieldname": "contract",
            "fieldtype": "Link",
            "options": "Rental Contract",
            "width": 150,
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
            "width": 160,
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
            "label": _("Rate"),
            "fieldname": "rate",
            "fieldtype": "Currency",
            "width": 110,
        },
        {
            "label": _("Period Type"),
            "fieldname": "period_type",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Duration"),
            "fieldname": "duration",
            "fieldtype": "Int",
            "width": 80,
        },
        {
            "label": _("Total Amount"),
            "fieldname": "total_amount",
            "fieldtype": "Currency",
            "width": 130,
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Rent to Own"),
            "fieldname": "rent_to_own",
            "fieldtype": "Check",
            "width": 90,
        },
    ]


def get_data(filters: dict | None = None) -> list[dict]:
    rc_filters = {"docstatus": 1}
    if filters:
        if filters.get("status"):
            rc_filters["status"] = filters["status"]
        if filters.get("customer"):
            rc_filters["customer"] = filters["customer"]
        if filters.get("vehicle"):
            rc_filters["vehicle"] = filters["vehicle"]

    contracts = frappe.db.get_all(
        "Rental Contract",
        filters=rc_filters,
        fields=[
            "name",
            "customer",
            "customer_name",
            "vehicle",
            "rate",
            "period_type",
            "duration",
            "total_amount",
            "status",
            "rent_to_own",
        ],
        order_by="name desc",
    )

    data = []
    for c in contracts:
        license_plate = frappe.db.get_value("Vehicle", c.vehicle, "license_plate") or ""
        data.append(
            {
                "contract": c.name,
                "customer": c.customer,
                "customer_name": c.customer_name,
                "vehicle": c.vehicle,
                "license_plate": license_plate,
                "rate": flt(c.rate),
                "period_type": c.period_type,
                "duration": c.duration,
                "total_amount": flt(c.total_amount),
                "status": c.status,
                "rent_to_own": c.rent_to_own,
            }
        )

    return data


def get_chart_data(data: list[dict]) -> dict:
    """Return status distribution for pie chart."""
    status_counts: dict[str, int] = {}
    for row in data:
        status = row.get("status") or "Unknown"
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
