# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

"""Vehicle-related whitelisted API methods for Stride."""

import frappe
from frappe.utils import flt


@frappe.whitelist()
def get_vehicle_payment_kpis(vehicle: str) -> dict:
    """Return payment KPI summary for a Vehicle.

    Aggregates data from all Lease Payment Schedule rows across
    submitted Leases linked to this Vehicle.

    Args:
            vehicle: Vehicle name/license plate.

    Returns:
            dict with counts and amounts by status (Pending, Invoiced, Paid, Overdue).
    """
    # Get all submitted leases for this vehicle
    leases = frappe.db.get_all(
        "Lease",
        filters={"vehicle": vehicle, "docstatus": 1},
        pluck="name",
    )

    if not leases:
        return {
            "total_periods": 0,
            "total_amount": 0,
            "statuses": {},
        }

    # Aggregate schedule rows across all leases
    schedule_rows = frappe.db.get_all(
        "Lease Payment Schedule",
        filters={
            "parent": ("in", leases),
            "parenttype": "Lease",
        },
        fields=["status", "amount"],
    )

    statuses: dict[str, dict] = {}
    total_amount = 0.0

    for row in schedule_rows:
        status = row.status
        amount = flt(row.amount)
        total_amount += amount

        if status not in statuses:
            statuses[status] = {"count": 0, "amount": 0.0}

        statuses[status]["count"] += 1
        statuses[status]["amount"] = flt(statuses[status]["amount"] + amount)

    return {
        "total_periods": len(schedule_rows),
        "total_amount": flt(total_amount),
        "statuses": statuses,
    }
