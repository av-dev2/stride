from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import flt, get_fullname, getdate, nowdate

RENTAL_MANAGER_ROLE = "Rental Manager"

LEASE_FIELDS = [
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
]


@frappe.whitelist()
def get_pwa_context() -> dict:
	"""Return all data required to render the Stride PWA customer dashboard.

	Flow:
	  1. Resolve the logged-in user to a Customer via the Portal User child table.
	     A user without a Customer link must have the Rental Manager role.
	  2. Fetch the customer's active Lease (docstatus == 1).
	  3. Build the dashboard context for that Lease (see `_build_lease_dashboard`).

	Returns:
	    dict with keys: customer, customer_name, lease, payments, vehicle, contract.
	"""
	user = _require_logged_in_user()

	# --- 1. Resolve Customer from Portal User child table ---
	customer = frappe.db.get_value("Portal User", {"user": user}, "parent")

	if not customer:
		is_manager = RENTAL_MANAGER_ROLE in frappe.get_roles(user)
		if not is_manager:
			frappe.throw(
				_(
					"Your account must be linked to a Customer or have the Rental Manager role to access this resource."
				),
				frappe.PermissionError,
			)
		return {
			"error": "no_customer",
			"is_manager": True,
			"logged_in_user_name": get_fullname(user),
			"message": _("Your account is not linked to a customer. Please contact your administrator."),
		}

	# --- 2. Fetch active Lease for this customer ---
	leases = frappe.db.get_all(
		"Lease",
		filters={"customer": customer, "docstatus": 1},
		fields=LEASE_FIELDS,
		order_by="creation desc",
		limit=1,
	)

	if not leases:
		return {
			"error": "no_lease",
			"customer": customer,
			"logged_in_user_name": get_fullname(user),
			"message": _("No active lease found for your account."),
		}

	return _build_lease_dashboard(leases[0], logged_in_user_name=get_fullname(user))


@frappe.whitelist()
def get_manager_vehicles() -> dict:
	"""Return the fleet vehicle list for the Rental Manager PWA view.

	Excludes vehicles whose latest submitted Lease is Completed, since a
	completed lease means the vehicle has already been handed over/returned
	and is no longer relevant to actively manage.
	"""
	user = _require_logged_in_user()
	_require_rental_manager(user)

	vehicles = frappe.db.get_all(
		"Vehicle",
		fields=["name", "license_plate", "make", "model", "vehicle_status", "vehicle_image"],
		order_by="modified desc",
	)

	latest_lease_by_vehicle = _get_latest_lease_by_vehicle([v.name for v in vehicles])

	rows = []
	for vehicle in vehicles:
		lease = latest_lease_by_vehicle.get(vehicle.name)
		if lease and lease.status == "Completed":
			continue

		rows.append(
			{
				**vehicle,
				"customer_name": lease.customer_name if lease else None,
				"contract_start": lease.start_date if lease else None,
				"contract_end": lease.end_date if lease else None,
			}
		)

	return {"vehicles": rows, "logged_in_user_name": get_fullname(user)}


@frappe.whitelist()
def get_vehicle_pwa_context(vehicle: str) -> dict:
	"""Return the dashboard context for one vehicle (Rental Manager PWA view).

	Mirrors `get_pwa_context`, but resolves the active Lease by vehicle
	instead of by the logged-in user's linked Customer.
	"""
	user = _require_logged_in_user()
	_require_rental_manager(user)

	leases = frappe.db.get_all(
		"Lease",
		filters={"vehicle": vehicle, "docstatus": 1},
		fields=LEASE_FIELDS,
		order_by="creation desc",
		limit=1,
	)

	if not leases:
		return {
			"error": "no_lease",
			"logged_in_user_name": get_fullname(user),
			"message": _("No active lease found for this vehicle."),
		}

	return _build_lease_dashboard(leases[0], logged_in_user_name=get_fullname(user))


def _require_logged_in_user() -> str:
	user = frappe.session.user

	if not user or user == "Guest":
		frappe.throw(_("You must be logged in to access this resource."), frappe.AuthenticationError)

	return user


def _require_rental_manager(user: str) -> None:
	if RENTAL_MANAGER_ROLE not in frappe.get_roles(user):
		frappe.throw(
			_("You must have the Rental Manager role to access this resource."),
			frappe.PermissionError,
		)


def _get_latest_lease_by_vehicle(vehicle_names: list[str]) -> dict:
	if not vehicle_names:
		return {}

	leases = frappe.db.get_all(
		"Lease",
		filters={"vehicle": ["in", vehicle_names], "docstatus": 1},
		fields=["vehicle", "customer_name", "start_date", "end_date", "status"],
		order_by="creation desc",
	)

	latest_by_vehicle = {}
	for lease in leases:
		latest_by_vehicle.setdefault(lease.vehicle, lease)
	return latest_by_vehicle


def _build_lease_dashboard(lease, logged_in_user_name: str) -> dict:
	"""Build the payments/vehicle/contract dashboard context for one Lease.

	Flow:
	  1. From the Lease's payment_schedule child table, count and list rows for:
	     - Paid      (status == 'Paid')
	     - Invoiced  (status == 'Invoiced')  ← shown as "Pending Payments" in UI
	     - Postponed (status == 'Postponed')
	     Rows with status == 'Pending' are intentionally excluded (no invoice yet).
	     Rows are ordered newest period first (idx desc).
	  2. Fetch Vehicle details linked to the Lease.
	  3. Fetch the active Rental Contract for supplementary context.
	"""
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
		order_by="idx desc",
	)

	paid_rows = [r for r in schedule_rows if r.status == "Paid"]
	invoiced_rows = [r for r in schedule_rows if r.status == "Invoiced"]
	postponed_rows = [r for r in schedule_rows if r.status == "Postponed"]

	payments = {
		"paid": {"count": len(paid_rows), "rows": paid_rows},
		"invoiced": {"count": len(invoiced_rows), "rows": invoiced_rows},
		"postponed": {"count": len(postponed_rows), "rows": postponed_rows},
	}

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
		"logged_in_user_name": logged_in_user_name,
		"lease": lease,
		"payments": payments,
		"vehicle": vehicle_data,
		"contract": contract,
	}
