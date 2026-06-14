# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

"""Vehicle Profit and Loss Report.

Shows revenue vs costs per vehicle using Lease payment data
and GL entries when available.
"""

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters: dict | None = None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


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
            "label": _("Total Revenue"),
            "fieldname": "total_revenue",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": _("Total Paid"),
            "fieldname": "total_paid",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": _("Outstanding"),
            "fieldname": "outstanding",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": _("Vehicle Value"),
            "fieldname": "vehicle_value",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": _("Profit/Loss"),
            "fieldname": "profit_loss",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": _("Active Leases"),
            "fieldname": "active_leases",
            "fieldtype": "Int",
            "width": 110,
        },
    ]


def get_data(filters: dict | None = None) -> list[dict]:
    conditions = {}
    if filters and filters.get("vehicle"):
        conditions["name"] = filters["vehicle"]

    vehicles = frappe.db.get_all(
        "Vehicle",
        filters=conditions,
        fields=["name", "license_plate", "make", "model", "vehicle_value"],
        order_by="name asc",
    )

    data = []
    for v in vehicles:
        # Aggregate from submitted leases for this vehicle
        leases = frappe.db.get_all(
            "Lease",
            filters={"vehicle": v.name, "docstatus": 1},
            fields=["total_amount", "total_paid", "total_outstanding"],
        )

        total_revenue = sum(flt(l.total_amount) for l in leases)
        total_paid = sum(flt(l.total_paid) for l in leases)
        outstanding = sum(flt(l.total_outstanding) for l in leases)
        vehicle_value = flt(v.vehicle_value)
        profit_loss = total_paid - vehicle_value

        data.append(
            {
                "vehicle": v.name,
                "license_plate": v.license_plate,
                "make": v.make,
                "model": v.model,
                "total_revenue": total_revenue,
                "total_paid": total_paid,
                "outstanding": outstanding,
                "vehicle_value": vehicle_value,
                "profit_loss": profit_loss,
                "active_leases": len(leases),
            }
        )

    return data
