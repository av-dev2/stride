from __future__ import annotations

import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from frappe import _
from frappe.utils import flt, get_fullname, getdate, nowdate

from stride.overrides.payment_entry import reconcile_lease_payments

RENTAL_MANAGER_ROLE = "Rental Manager"


@frappe.whitelist()
def get_payment_form_options() -> dict:
	"""Return Company/Mode of Payment choices for the manager 'Make Payment' dialog.

	Uses `frappe.get_list` (not `frappe.db.get_all`) so results are filtered by
	the caller's own read permission on Company and Mode of Payment.
	"""
	user = _require_rental_manager()

	companies = frappe.get_list("Company", fields=["name"], order_by="name asc", limit=0)
	modes_of_payment = frappe.get_list("Mode of Payment", fields=["name"], order_by="name asc", limit=0)

	return {
		"companies": [c.name for c in companies],
		"modes_of_payment": [m.name for m in modes_of_payment],
		"default_company": frappe.defaults.get_user_default("Company")
		or (companies[0].name if companies else None),
		"logged_in_user_name": get_fullname(user),
	}


@frappe.whitelist()
def create_manager_payment(
	vehicle: str,
	company: str,
	mode_of_payment: str,
	paid_amount,
	posting_date: str | None = None,
) -> dict:
	"""Create and submit a Payment Entry against a vehicle's oldest pending invoices.

	Selects the oldest Invoiced Lease Payment Schedule rows for the vehicle's
	active Lease (FIFO by due date) whose cumulative outstanding fits within
	`paid_amount`, then builds and submits one Payment Entry referencing those
	Sales Invoices. Runs under the caller's own Frappe permissions throughout
	(no `ignore_permissions`), so it fails with Frappe's normal permission
	error if the Rental Manager role hasn't been granted the required DocType
	permissions (create/submit on Payment Entry, read on Sales Invoice/Mode of
	Payment/Company).
	"""
	_require_rental_manager()

	paid_amount = flt(paid_amount)
	if paid_amount <= 0:
		frappe.throw(_("Paid amount must be greater than zero."))

	if not frappe.has_permission("Sales Invoice", "read"):
		frappe.throw(_("You do not have permission to read Sales Invoice."), frappe.PermissionError)

	lease = _get_active_lease(vehicle)
	selected_invoices, allocated_amount = _select_fifo_invoices(lease.name, paid_amount)

	payment_entry = _build_payment_entry(
		selected_invoices, company, mode_of_payment, posting_date, allocated_amount
	)
	payment_entry.insert()
	payment_entry.submit()

	reconcile_lease_payments(payment_entry)

	return {
		"payment_entry": payment_entry.name,
		"invoices_paid": [invoice.name for invoice in selected_invoices],
		"amount_allocated": allocated_amount,
		"unallocated_amount": paid_amount - allocated_amount,
	}


def _require_rental_manager() -> str:
	user = frappe.session.user

	if not user or user == "Guest":
		frappe.throw(_("You must be logged in to access this resource."), frappe.AuthenticationError)

	if RENTAL_MANAGER_ROLE not in frappe.get_roles(user):
		frappe.throw(
			_("You must have the Rental Manager role to access this resource."),
			frappe.PermissionError,
		)

	return user


def _get_active_lease(vehicle: str):
	leases = frappe.db.get_all(
		"Lease",
		filters={"vehicle": vehicle, "docstatus": 1},
		fields=["name", "customer"],
		order_by="creation desc",
		limit=1,
	)
	if not leases:
		frappe.throw(_("No active lease found for this vehicle."))
	return leases[0]


def _select_fifo_invoices(lease_name: str, paid_amount: float) -> tuple[list, float]:
	"""Pick the oldest Invoiced schedule rows' Sales Invoices that fit within paid_amount."""
	schedule_rows = frappe.db.get_all(
		"Lease Payment Schedule",
		filters={"parent": lease_name, "parenttype": "Lease", "status": "Invoiced"},
		fields=["sales_invoice"],
		order_by="due_date asc",
	)
	invoice_order = [row.sales_invoice for row in schedule_rows if row.sales_invoice]
	if not invoice_order:
		frappe.throw(_("There are no pending invoices for this vehicle."))

	invoices = frappe.get_list(
		"Sales Invoice",
		filters={"name": ["in", invoice_order], "docstatus": 1, "outstanding_amount": [">", 0]},
		fields=["name", "outstanding_amount", "grand_total", "due_date"],
		limit=0,
	)
	order_index = {name: idx for idx, name in enumerate(invoice_order)}
	invoices.sort(key=lambda invoice: order_index.get(invoice.name, 0))

	selected = []
	running_total = 0.0
	for invoice in invoices:
		if flt(running_total + invoice.outstanding_amount, 2) > flt(paid_amount, 2):
			break
		running_total += flt(invoice.outstanding_amount)
		selected.append(invoice)

	if not selected:
		frappe.throw(_("The paid amount is not enough to cover the oldest outstanding invoice."))

	return selected, running_total


def _build_payment_entry(selected_invoices, company, mode_of_payment, posting_date, allocated_amount):
	first_invoice = selected_invoices[0]
	payment_entry = get_payment_entry(
		"Sales Invoice", first_invoice.name, party_amount=first_invoice.outstanding_amount
	)
	payment_entry.company = company
	payment_entry.posting_date = getdate(posting_date) if posting_date else nowdate()
	payment_entry.mode_of_payment = mode_of_payment

	bank_account = get_bank_cash_account(mode_of_payment, company)
	payment_entry.paid_to = bank_account["account"]
	payment_entry.paid_to_account_currency = frappe.get_cached_value(
		"Account", bank_account["account"], "account_currency"
	)

	for invoice in selected_invoices[1:]:
		payment_entry.append(
			"references",
			{
				"reference_doctype": "Sales Invoice",
				"reference_name": invoice.name,
				"due_date": invoice.due_date,
				"total_amount": invoice.grand_total,
				"outstanding_amount": invoice.outstanding_amount,
				"allocated_amount": invoice.outstanding_amount,
			},
		)

	payment_entry.paid_amount = allocated_amount
	payment_entry.received_amount = allocated_amount

	return payment_entry
