# Copyright (c) 2026, elius-dev and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import today

from stride.api.pwa import get_manager_vehicles, get_pwa_context, get_vehicle_pwa_context
from stride.tests.utils import get_or_create_customer, get_or_create_vehicle, make_rental_contract


def make_portal_user(customer: str, user: str) -> None:
	customer_doc = frappe.get_doc("Customer", customer)
	if not any(row.user == user for row in customer_doc.get("portal_users", [])):
		customer_doc.append("portal_users", {"user": user})
		customer_doc.save(ignore_permissions=True)


def make_rental_manager_user(email: str) -> str:
	if not frappe.db.exists("Role", "Rental Manager"):
		frappe.get_doc({"doctype": "Role", "role_name": "Rental Manager"}).insert(ignore_permissions=True)

	if not frappe.db.exists("User", email):
		frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": "Stride Rental Manager",
				"send_welcome_email": 0,
			}
		).insert(ignore_permissions=True)

	user = frappe.get_doc("User", email)
	if not any(row.role == "Rental Manager" for row in user.get("roles", [])):
		user.append("roles", {"role": "Rental Manager"})
		user.save(ignore_permissions=True)

	return email


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


class TestManagerVehicleViews(IntegrationTestCase):
	def tearDown(self):
		frappe.set_user("Administrator")

	def test_non_manager_is_rejected_from_manager_endpoints(self):
		user = "stride-pwa-non-manager@example.com"
		if not frappe.db.exists("User", user):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": user,
					"first_name": "Stride PWA Non Manager",
					"send_welcome_email": 0,
				}
			).insert(ignore_permissions=True)
		self.addCleanup(frappe.set_user, "Administrator")

		frappe.set_user(user)
		with self.assertRaises(frappe.PermissionError):
			get_manager_vehicles()

	def test_manager_sees_vehicle_with_active_lease_and_excludes_completed(self):
		manager = make_rental_manager_user("stride-pwa-manager@example.com")
		self.addCleanup(frappe.set_user, "Administrator")

		customer = get_or_create_customer("Stride PWA Manager Customer")
		active_vehicle = get_or_create_vehicle("STRIDE-TEST-PWA-002")
		completed_vehicle = get_or_create_vehicle("STRIDE-TEST-PWA-003")

		active_contract = make_rental_contract(active_vehicle, customer)
		active_contract.submit()
		active_lease = frappe.new_doc("Lease")
		active_lease.rental_contract = active_contract.name
		active_lease.vehicle = active_vehicle
		active_lease.customer = customer
		active_lease.start_date = today()
		active_lease.rate = 100
		active_lease.period_type = "Daily"
		active_lease.duration = 2
		active_lease.insert(ignore_permissions=True)
		active_lease.submit()
		self.addCleanup(lambda: frappe.db.set_value("Lease", active_lease.name, "docstatus", 2))

		completed_contract = make_rental_contract(completed_vehicle, customer)
		completed_contract.submit()
		completed_lease = frappe.new_doc("Lease")
		completed_lease.rental_contract = completed_contract.name
		completed_lease.vehicle = completed_vehicle
		completed_lease.customer = customer
		completed_lease.start_date = today()
		completed_lease.rate = 100
		completed_lease.period_type = "Daily"
		completed_lease.duration = 2
		completed_lease.insert(ignore_permissions=True)
		completed_lease.submit()
		frappe.db.set_value("Lease", completed_lease.name, "status", "Completed")
		self.addCleanup(lambda: frappe.db.set_value("Lease", completed_lease.name, "docstatus", 2))

		frappe.set_user(manager)
		vehicle_names = {row["name"] for row in get_manager_vehicles()["vehicles"]}
		self.assertIn(active_vehicle, vehicle_names)
		self.assertNotIn(completed_vehicle, vehicle_names)

		result = get_vehicle_pwa_context(active_vehicle)
		self.assertNotIn("error", result)
		self.assertEqual(result["lease"]["name"], active_lease.name)
		self.assertEqual(result["customer_name"], customer)
