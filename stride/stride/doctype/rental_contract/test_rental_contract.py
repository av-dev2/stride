# Copyright (c) 2026, elius-dev and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import today

from stride.tests.utils import get_or_create_customer, get_or_create_vehicle, make_rental_contract


class TestRentalContract(IntegrationTestCase):
	def setUp(self):
		self.customer = get_or_create_customer("Stride Test Customer")

	def test_total_amount_is_rate_times_duration(self):
		vehicle = get_or_create_vehicle("STRIDE-TEST-RC-001")
		contract = make_rental_contract(vehicle, self.customer, rate=100, duration=10)
		self.assertEqual(contract.total_amount, 1000)

	def test_vehicle_must_be_available(self):
		vehicle = get_or_create_vehicle("STRIDE-TEST-RC-002", status="Rented")
		with self.assertRaises(frappe.ValidationError):
			make_rental_contract(vehicle, self.customer)

	def test_cannot_cancel_with_active_lease(self):
		vehicle = get_or_create_vehicle("STRIDE-TEST-RC-003")
		contract = make_rental_contract(vehicle, self.customer)
		contract.submit()

		lease = frappe.new_doc("Lease")
		lease.rental_contract = contract.name
		lease.vehicle = vehicle
		lease.start_date = today()
		lease.rate = 100
		lease.period_type = "Daily"
		lease.duration = 10
		lease.insert(ignore_permissions=True)
		lease.submit()
		self.addCleanup(lambda: frappe.db.set_value("Lease", lease.name, "docstatus", 2))

		with self.assertRaises(frappe.ValidationError):
			contract.cancel()

	def test_contract_template_renders_into_content(self):
		if not frappe.db.exists("Contract Template", {"is_default": 1}):
			self.skipTest("No default Contract Template configured on this site")

		vehicle = get_or_create_vehicle("STRIDE-TEST-RC-004")
		template_name = frappe.db.get_value("Contract Template", {"is_default": 1}, "name")
		contract = make_rental_contract(vehicle, self.customer, contract_template=template_name)

		self.assertTrue(contract.contract_content)
