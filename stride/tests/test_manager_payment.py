# Copyright (c) 2026, elius-dev and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import today

from stride.api.manager_payment import create_manager_payment, get_payment_form_options
from stride.tasks import _create_sales_invoice_for_row
from stride.tests.utils import (
	get_default_test_company,
	get_or_create_customer,
	get_or_create_rental_service_item,
	get_or_create_vehicle,
	make_rental_contract,
)


def make_lease_with_invoiced_rows(suffix: str, periods: int, rate: float = 100):
	"""Build a submitted Lease with every schedule row already invoiced.

	Returns (lease, vehicle_name).
	"""
	customer = get_or_create_customer(f"Stride Manager Payment Customer {suffix}")
	vehicle = get_or_create_vehicle(f"STRIDE-TEST-MGRPAY-{suffix}")
	rental_service = get_or_create_rental_service_item()
	frappe.db.set_value("Vehicle", vehicle, "rental_service", rental_service)

	contract = make_rental_contract(
		vehicle,
		customer,
		duration=periods,
		rate=rate,
		company=get_default_test_company(),
	)
	contract.submit()

	lease = frappe.new_doc("Lease")
	lease.rental_contract = contract.name
	lease.vehicle = vehicle
	lease.customer = customer
	lease.start_date = today()
	lease.insert(ignore_permissions=True)
	lease.submit()

	lease.reload()
	for row in lease.payment_schedule:
		_create_sales_invoice_for_row(row)

	lease.reload()
	return lease, vehicle


def make_user_without_permissions(email: str, first_name: str, roles: list[str]) -> str:
	if not frappe.db.exists("User", email):
		frappe.get_doc(
			{"doctype": "User", "email": email, "first_name": first_name, "send_welcome_email": 0}
		).insert(ignore_permissions=True)

	user = frappe.get_doc("User", email)
	for role in roles:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role}).insert(ignore_permissions=True)
		if not any(r.role == role for r in user.get("roles", [])):
			user.append("roles", {"role": role})
	user.save(ignore_permissions=True)
	return email


class TestManagerPayment(IntegrationTestCase):
	def tearDown(self):
		frappe.set_user("Administrator")

	def test_non_manager_is_rejected(self):
		user = make_user_without_permissions("stride-mgrpay-norole@example.com", "No Role", roles=[])
		frappe.set_user(user)

		with self.assertRaises(frappe.PermissionError):
			get_payment_form_options()

		with self.assertRaises(frappe.PermissionError):
			create_manager_payment(
				vehicle="does-not-matter",
				company="does-not-matter",
				mode_of_payment="does-not-matter",
				paid_amount=100,
			)

	def test_manager_without_payment_entry_permission_is_rejected(self):
		lease, vehicle = make_lease_with_invoiced_rows("PERM", periods=1)
		self.addCleanup(lambda: frappe.db.set_value("Lease", lease.name, "docstatus", 2))

		user = make_user_without_permissions(
			"stride-mgrpay-manager-noperm@example.com", "Manager No Perm", roles=["Rental Manager"]
		)
		frappe.set_user(user)

		with self.assertRaises(frappe.PermissionError):
			create_manager_payment(
				vehicle=vehicle,
				company=get_default_test_company(),
				mode_of_payment="Cash",
				paid_amount=100,
			)

	def test_manager_payment_selects_oldest_invoices_first(self):
		lease, vehicle = make_lease_with_invoiced_rows("FIFO", periods=3, rate=100)
		self.addCleanup(lambda: frappe.db.set_value("Lease", lease.name, "docstatus", 2))

		rows_before = sorted(lease.payment_schedule, key=lambda r: r.due_date)
		oldest_two = [rows_before[0].sales_invoice, rows_before[1].sales_invoice]

		result = create_manager_payment(
			vehicle=vehicle,
			company=get_default_test_company(),
			mode_of_payment="Cash",
			paid_amount=250,
		)
		self.addCleanup(lambda: frappe.db.set_value("Payment Entry", result["payment_entry"], "docstatus", 2))

		self.assertEqual(sorted(result["invoices_paid"]), sorted(oldest_two))
		self.assertEqual(result["amount_allocated"], 200)
		self.assertEqual(result["unallocated_amount"], 50)

		lease.reload()
		rows_after = sorted(lease.payment_schedule, key=lambda r: r.due_date)
		self.assertEqual(rows_after[0].status, "Paid")
		self.assertEqual(rows_after[1].status, "Paid")
		self.assertEqual(rows_after[2].status, "Invoiced")
