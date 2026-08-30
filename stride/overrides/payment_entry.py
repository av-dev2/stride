# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

"""Payment Entry hooks for Stride lease payment reconciliation."""

import frappe
from frappe.utils import flt


def on_submit(doc, method: str) -> None:
	"""Update Lease Payment Schedule rows to 'Paid' when payment is received.

	Triggered via doc_events["Payment Entry"]["on_submit"].
	Only runs if 'Enable Auto Reconciliation' is ticked in Stride Settings.

	Logic:
	1. Look at the Payment Entry's references (linked Sales Invoices).
	2. For each Sales Invoice, check if it's linked to a Lease Payment Schedule row.
	3. If yes, mark that schedule row as 'Paid' and link the Payment Entry.
	4. Update Lease totals (total_paid, total_outstanding).
	"""
	if not _is_auto_reconciliation_enabled():
		return

	reconcile_lease_payments(doc)


def on_cancel(doc, method: str) -> None:
	"""Revert Lease Payment Schedule rows to 'Invoiced' when payment is cancelled.

	Triggered via doc_events["Payment Entry"]["on_cancel"].
	Only runs if 'Enable Auto Reconciliation' is ticked in Stride Settings.
	"""
	if not _is_auto_reconciliation_enabled():
		return

	_unreconcile_lease_payments(doc)


def _is_auto_reconciliation_enabled() -> bool:
	"""Check if auto-reconciliation is enabled in Stride Settings."""
	return bool(frappe.db.get_single_value("Stride Settings", "enable_auto_reconciliation"))


def reconcile_lease_payments(payment_entry) -> None:
	"""Mark schedule rows as Paid for invoices referenced in this Payment Entry."""
	affected_leases = set()

	for ref in payment_entry.get("references", []):
		if ref.reference_doctype != "Sales Invoice" or not ref.reference_name:
			continue

		# Find schedule rows linked to this Sales Invoice
		schedule_rows = frappe.db.get_all(
			"Lease Payment Schedule",
			filters={
				"parenttype": "Lease",
				"sales_invoice": ref.reference_name,
				"status": "Invoiced",
			},
			fields=["name", "parent"],
		)

		for row in schedule_rows:
			frappe.db.set_value(
				"Lease Payment Schedule",
				row.name,
				{
					"status": "Paid",
					"payment_entry": payment_entry.name,
				},
			)
			affected_leases.add(row.parent)

	# Update totals on affected leases
	for lease_name in affected_leases:
		_update_lease_totals(lease_name)


def _unreconcile_lease_payments(payment_entry) -> None:
	"""Revert schedule rows back to Invoiced when payment is cancelled."""
	affected_leases = set()

	# Find all schedule rows that reference this Payment Entry
	schedule_rows = frappe.db.get_all(
		"Lease Payment Schedule",
		filters={
			"parenttype": "Lease",
			"payment_entry": payment_entry.name,
			"status": "Paid",
		},
		fields=["name", "parent"],
	)

	for row in schedule_rows:
		frappe.db.set_value(
			"Lease Payment Schedule",
			row.name,
			{
				"status": "Invoiced",
				"payment_entry": "",
			},
		)
		affected_leases.add(row.parent)

	for lease_name in affected_leases:
		_update_lease_totals(lease_name)


def _update_lease_totals(lease_name: str) -> None:
	"""Recalculate total_paid and total_outstanding on a Lease."""
	total_paid = (
		frappe.db.get_value(
			"Lease Payment Schedule",
			filters={
				"parent": lease_name,
				"parenttype": "Lease",
				"status": "Paid",
			},
			fieldname=[{"SUM": "amount"}],
		)
		or 0
	)

	total_amount = flt(frappe.db.get_value("Lease", lease_name, "total_amount"))
	total_outstanding = flt(total_amount) - flt(total_paid)

	frappe.db.set_value(
		"Lease",
		lease_name,
		{
			"total_paid": flt(total_paid),
			"total_outstanding": flt(total_outstanding),
		},
	)

	# If all payments are done, mark lease as Completed
	pending_count = frappe.db.count(
		"Lease Payment Schedule",
		filters={
			"parent": lease_name,
			"parenttype": "Lease",
			"status": ("!=", "Paid"),
		},
	)

	if pending_count == 0 and flt(total_paid) > 0:
		frappe.db.set_value("Lease", lease_name, "status", "Completed")
