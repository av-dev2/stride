# Copyright (c) 2026, elius-dev and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import today

from stride.api.pwa import get_pwa_context
from stride.tests.utils import get_or_create_customer, get_or_create_vehicle, make_rental_contract


def make_portal_user(customer: str, user: str) -> None:
	customer_doc = frappe.get_doc("Customer", customer)
	if not any(row.user == user for row in customer_doc.get("portal_users", [])):
		customer_doc.append("portal_users", {"user": user})
		customer_doc.save(ignore_permissions=True)


class TestGetPwaContext(IntegrationTestCase):
	def tearDown(self):
		frappe.set_user("Administrator")

	def test_guest_is_rejected(self):
		frappe.set_user("Guest")
		with self.assertRaises(frappe.AuthenticationError):
			get_pwa_context()

	def test_user_without_customer_link_gets_no_customer_error(self):
		frappe.set_user("Administrator")
		if frappe.db.exists("Portal User", {"user": "Administrator"}):
			self.skipTest("Administrator is already linked to a customer on this site")

		result = get_pwa_context()
		self.assertEqual(result["error"], "no_customer")

	def test_user_without_customer_link_or_role_is_rejected(self):
		user = "stride-pwa-no-role@example.com"
		if not frappe.db.exists("User", user):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": user,
					"first_name": "Stride PWA No Role",
					"send_welcome_email": 0,
				}
			).insert(ignore_permissions=True)
		self.addCleanup(frappe.set_user, "Administrator")

		frappe.set_user(user)
		with self.assertRaises(frappe.PermissionError):
			get_pwa_context()

	def test_customer_without_lease_gets_no_lease_error(self):
		customer = get_or_create_customer("Stride PWA Customer No Lease")
		make_portal_user(customer, "Administrator")
		self.addCleanup(frappe.set_user, "Administrator")

		frappe.set_user("Administrator")
		result = get_pwa_context()
		self.assertEqual(result["error"], "no_lease")
		self.assertEqual(result["customer"], customer)

	def test_customer_with_active_lease_returns_payments_and_vehicle(self):
		customer = get_or_create_customer("Stride PWA Customer With Lease")
		make_portal_user(customer, "Administrator")
		self.addCleanup(frappe.set_user, "Administrator")

		vehicle = get_or_create_vehicle("STRIDE-TEST-PWA-001")
		contract = make_rental_contract(vehicle, customer)
		contract.submit()

		lease = frappe.new_doc("Lease")
		lease.rental_contract = contract.name
		lease.vehicle = vehicle
		lease.customer = customer
		lease.start_date = today()
		lease.rate = 100
		lease.period_type = "Daily"
		lease.duration = 2
		lease.insert(ignore_permissions=True)
		lease.submit()
		self.addCleanup(lambda: frappe.db.set_value("Lease", lease.name, "docstatus", 2))

		frappe.set_user("Administrator")
		result = get_pwa_context()

		self.assertNotIn("error", result)
		self.assertEqual(result["lease"]["name"], lease.name)
		self.assertEqual(result["vehicle"]["name"], vehicle)
		self.assertIn("paid", result["payments"])
		self.assertIn("invoiced", result["payments"])
		self.assertIn("postponed", result["payments"])
