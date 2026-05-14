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

	frappe.msgprint(
		_("Vehicle has been registered as an Accounting Dimension."),
		indicator="green",
	)
