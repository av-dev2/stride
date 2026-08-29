from __future__ import annotations

import frappe
from frappe import _


@frappe.whitelist()
def get_pwa_context() -> dict:
	"""Return all data required to render the Stride PWA dashboard.

	Flow:
	  1. Resolve the logged-in user to a Customer via the Portal User child table.
	  2. Fetch the customer's active Lease (docstatus == 1).
	  3. From the Lease's payment_schedule child table, count and list rows for:
	     - Paid      (status == 'Paid')
	     - Invoiced  (status == 'Invoiced')  ← shown as "Pending Payments" in UI
	     - Postponed (status == 'Postponed')
	     Rows with status == 'Pending' are intentionally excluded (no invoice yet).
	  4. Fetch Vehicle details linked to the Lease.
	  5. Fetch the active Rental Contract for supplementary context.

	Returns:
	    dict with keys: customer, customer_name, lease, payments, vehicle, contract.
	"""
	user = frappe.session.user

	if not user or user == "Guest":
		frappe.throw(_("You must be logged in to access this resource."), frappe.AuthenticationError)

	# --- 1. Resolve Customer from Portal User child table ---
	customer = frappe.db.get_value("Portal User", {"user": user}, "parent")

	if not customer:
		return {
			"error": "no_customer",
			"message": _("Your account is not linked to a customer. Please contact your administrator."),
		}

	# --- 2. Fetch active Lease for this customer ---
	leases = frappe.db.get_all(
		"Lease",
		filters={"customer": customer, "docstatus": 1},
		fields=[
			"name",
			"customer",
			"customer_name",
			"vehicle",
			"status",
			"start_date",
			"end_date",
			"rate",
			"period_type",
			"total_amount",
			"total_paid",
			"total_outstanding",
			"rental_contract",
		],
		order_by="creation desc",
		limit=1,
	)

	if not leases:
		return {
			"error": "no_lease",
			"customer": customer,
			"message": _("No active lease found for your account."),
		}

	lease = leases[0]

	# --- 3. Fetch payment schedule rows (exclude raw 'Pending' = no invoice yet) ---
	schedule_rows = frappe.db.get_all(
		"Lease Payment Schedule",
		filters={
			"parent": lease.name,
			"parenttype": "Lease",
			"status": ["in", ["Paid", "Invoiced", "Postponed"]],
		},
		fields=[
			"name",
			"idx",
			"from_date",
			"to_date",
			"due_date",
			"period",
			"amount",
			"status",
			"sales_invoice",
			"payment_entry",
		],
		order_by="idx asc",
	)

	# Categorise rows
	paid_rows = [r for r in schedule_rows if r.status == "Paid"]
	invoiced_rows = [r for r in schedule_rows if r.status == "Invoiced"]
	postponed_rows = [r for r in schedule_rows if r.status == "Postponed"]

	payments = {
		"paid": {
			"count": len(paid_rows),
			"rows": paid_rows,
		},
		"invoiced": {
			"count": len(invoiced_rows),
			"rows": invoiced_rows,
		},
		"postponed": {
			"count": len(postponed_rows),
			"rows": postponed_rows,
		},
	}

	# --- 4. Fetch Vehicle details ---
	vehicle_data = None
	if lease.vehicle:
		vehicle_data = frappe.db.get_value(
			"Vehicle",
			lease.vehicle,
			[
				"name",
				"license_plate",
				"make",
				"model",
				"year_of_manufacture",
				"color",
				"vehicle_status",
				"vehicle_image",
				"chassis_no",
				"fuel_type",
			],
			as_dict=True,
		)

	# --- 5. Fetch active Rental Contract for supplementary context ---
	contract = None
	if lease.rental_contract:
		contract = frappe.db.get_value(
			"Rental Contract",
			lease.rental_contract,
			[
				"name",
				"status",
				"rate",
				"period_type",
				"duration",
				"total_amount",
				"customer_identification_type",
				"customer_identification_no",
			],
			as_dict=True,
		)

	return {
		"customer": lease.customer,
		"customer_name": lease.customer_name,
		"lease": lease,
		"payments": payments,
		"vehicle": vehicle_data,
		"contract": contract,
	}
