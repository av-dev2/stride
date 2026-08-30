# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

"""Post-install setup for the Stride app."""

import frappe
from frappe import _


def after_install() -> None:
	"""Run after app installation on a site."""
	_create_vehicle_accounting_dimension()


def _create_vehicle_accounting_dimension() -> None:
	"""Register Vehicle as an Accounting Dimension.

	This allows Vehicle to be tracked on accounting transactions
	(Sales Invoice, Journal Entry, Payment Entry, etc.) so that
	per-vehicle P&L and financial reports can be generated.

	The ERPNext Accounting Dimension framework handles:
	- Adding a 'Vehicle' Link field to all relevant accounting doctypes
	- Budget tracking by Vehicle
	- Dimension-based reporting
	"""
	if frappe.db.exists("Accounting Dimension", {"document_type": "Vehicle"}):
		frappe.msgprint(
			_("Vehicle is already registered as an Accounting Dimension."),
			indicator="blue",
		)
		return

	dimension = frappe.new_doc("Accounting Dimension")
	dimension.document_type = "Vehicle"
	dimension.insert(ignore_permissions=True)

	# Accounting Dimension.on_update() enqueues the actual custom-field creation
	# on the "long" queue. Run it synchronously too so a Vehicle-linked Sales
	# Invoice/Payment Entry doesn't fail with "Unknown column 'vehicle'" when
	# no background worker has processed that job yet (e.g. right after install).
	from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
		make_dimension_in_accounting_doctypes,
	)

	make_dimension_in_accounting_doctypes(dimension)

	frappe.msgprint(
		_("Vehicle has been registered as an Accounting Dimension."),
		indicator="green",
	)
