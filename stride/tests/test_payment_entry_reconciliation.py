# Copyright (c) 2026, elius-dev and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import today

from stride.tasks import _create_sales_invoice_for_row
from stride.tests.utils import (
	get_default_test_company,
	get_or_create_customer,
	get_or_create_rental_service_item,
	get_or_create_vehicle,
	make_rental_contract,
)


def make_active_lease_with_invoice(suffix: str):
	"""Build a submitted Lease with one schedule row already invoiced.

	Returns (lease, schedule_row_name, sales_invoice_name).
	"""
	customer = get_or_create_customer(f"Stride Reconciliation Customer {suffix}")
	vehicle = get_or_create_vehicle(f"STRIDE-TEST-RECON-{suffix}")
	rental_service = get_or_create_rental_service_item()
	frappe.db.set_value("Vehicle", vehicle, "rental_service", rental_service)

	contract = make_rental_contract(vehicle, customer, duration=2, company=get_default_test_company())
	contract.submit()

	lease = frappe.new_doc("Lease")
	lease.rental_contract = contract.name
	lease.vehicle = vehicle
	lease.customer = customer
	lease.start_date = today()
	lease.insert(ignore_permissions=True)
	lease.submit()

	lease.reload()
	row = lease.payment_schedule[0]
	_create_sales_invoice_for_row(row)

	lease.reload()
	row = lease.payment_schedule[0]
	return lease, row.name, row.sales_invoice


class TestPaymentEntryReconciliation(IntegrationTestCase):
	def setUp(self):
		settings = frappe.get_single("Stride Settings")
		self._auto_reconciliation_was = settings.enable_auto_reconciliation
		settings.enable_auto_reconciliation = 1
		settings.save(ignore_permissions=True)

	def tearDown(self):
		settings = frappe.get_single("Stride Settings")
		settings.enable_auto_reconciliation = self._auto_reconciliation_was
		settings.save(ignore_permissions=True)

	def test_submitting_payment_entry_marks_schedule_row_paid(self):
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

		lease, row_name, sales_invoice = make_active_lease_with_invoice("A")

		pe = get_payment_entry("Sales Invoice", sales_invoice)
		pe.insert(ignore_permissions=True)
		pe.submit()
		self.addCleanup(lambda: frappe.db.set_value("Payment Entry", pe.name, "docstatus", 2))
		self.addCleanup(lambda: frappe.db.set_value("Lease", lease.name, "docstatus", 2))

		row = frappe.get_doc("Lease Payment Schedule", row_name)
		self.assertEqual(row.status, "Paid")
		self.assertEqual(row.payment_entry, pe.name)

		lease.reload()
		self.assertEqual(lease.total_paid, row.amount)

	def test_cancelling_payment_entry_reverts_schedule_row(self):
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

		lease, row_name, sales_invoice = make_active_lease_with_invoice("B")

		pe = get_payment_entry("Sales Invoice", sales_invoice)
		pe.insert(ignore_permissions=True)
		pe.submit()
		self.addCleanup(lambda: frappe.db.set_value("Lease", lease.name, "docstatus", 2))

		pe.cancel()

		row = frappe.get_doc("Lease Payment Schedule", row_name)
		self.assertEqual(row.status, "Invoiced")
		self.assertFalse(row.payment_entry)
