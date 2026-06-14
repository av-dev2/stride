# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

"""Overdue Payments Report.

Shows overdue Lease Payment Schedule rows with aging
(days past due) and customer/vehicle details.
"""

import frappe
from frappe import _
from frappe.utils import date_diff, flt, getdate, today


def execute(filters: dict | None = None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    return columns, data, None, chart


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
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 130,
        },
        {
            "label": _("Customer Name"),
            "fieldname": "customer_name",
            "fieldtype": "Data",
            "width": 150,
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
            "label": _("Period"),
            "fieldname": "period",
            "fieldtype": "Int",
            "width": 70,
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
            "label": _("Days Overdue"),
            "fieldname": "days_overdue",
            "fieldtype": "Int",
            "width": 110,
        },
        {
            "label": _("Aging Bucket"),
            "fieldname": "aging_bucket",
            "fieldtype": "Data",
            "width": 120,
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
        if filters.get("customer"):
            lease_filters["customer"] = filters["customer"]
        if filters.get("vehicle"):
            lease_filters["vehicle"] = filters["vehicle"]

    leases = frappe.db.get_all(
        "Lease",
        filters=lease_filters,
        fields=["name", "vehicle", "customer", "customer_name"],
    )

    if not leases:
        return []

    current_date = getdate(today())
    data = []

    for lease in leases:
        license_plate = frappe.db.get_value("Vehicle", lease.vehicle, "license_plate") or ""

        # Get overdue payment schedule rows (Pending/Invoiced with due_date < today)
        rows = frappe.db.get_all(
            "Lease Payment Schedule",
            filters={
                "parent": lease.name,
                "status": ("in", ["Pending", "Invoiced", "Overdue"]),
                "due_date": ("<", current_date),
            },
            fields=[
                "period",
                "due_date",
                "amount",
                "status",
                "sales_invoice",
            ],
            order_by="due_date asc",
        )

        for row in rows:
            days_overdue = date_diff(current_date, getdate(row.due_date))
            aging_bucket = _get_aging_bucket(days_overdue)

            # Apply min_days_overdue filter if specified
            if filters and filters.get("min_days_overdue"):
                if days_overdue < int(filters["min_days_overdue"]):
                    continue

            data.append(
                {
                    "lease": lease.name,
                    "customer": lease.customer,
                    "customer_name": lease.customer_name,
                    "vehicle": lease.vehicle,
                    "license_plate": license_plate,
                    "period": row.period,
                    "due_date": row.due_date,
                    "amount": flt(row.amount),
                    "days_overdue": days_overdue,
                    "aging_bucket": aging_bucket,
                    "sales_invoice": row.sales_invoice,
                }
            )

    # Sort by days overdue descending (worst first)
    data.sort(key=lambda x: x["days_overdue"], reverse=True)
    return data


def _get_aging_bucket(days: int) -> str:
    """Categorize overdue days into aging buckets."""
    if days <= 30:
        return "0-30 days"
    elif days <= 60:
        return "31-60 days"
    elif days <= 90:
        return "61-90 days"
    else:
        return "90+ days"


def get_chart_data(data: list[dict]) -> dict:
    """Return aging distribution bar chart."""
    buckets = {"0-30 days": 0, "31-60 days": 0, "61-90 days": 0, "90+ days": 0}

    for row in data:
        bucket = row.get("aging_bucket", "0-30 days")
        buckets[bucket] = buckets.get(bucket, 0) + flt(row.get("amount"))

    if not any(buckets.values()):
        return {}

    return {
        "data": {
            "labels": list(buckets.keys()),
            "datasets": [{"name": _("Overdue Amount"), "values": list(buckets.values())}],
        },
        "type": "bar",
        "colors": ["#ff5858"],
        "height": 280,
    }
