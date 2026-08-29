# Copyright (c) 2026, elius-dev and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, getdate, today

from stride.tests.utils import get_or_create_customer, get_or_create_vehicle, make_rental_contract


def make_lease(rental_contract: str, vehicle: str, **overrides):
	# vehicle/rate/period_type/duration are fetch_from(rental_contract) on Lease,
	# so only start_date is meaningfully settable here.
	lease = frappe.new_doc("Lease")
	lease.rental_contract = rental_contract
	lease.vehicle = vehicle
	lease.start_date = today()
	lease.update(overrides)
	lease.insert(ignore_permissions=True)
	return lease


class TestLease(IntegrationTestCase):
	def setUp(self):
		self.customer = get_or_create_customer("Stride Test Customer")

	def test_requires_a_submitted_rental_contract(self):
		vehicle = get_or_create_vehicle("STRIDE-TEST-LS-001")
		draft_contract = make_rental_contract(vehicle, self.customer)

		with self.assertRaises(frappe.ValidationError):
			make_lease(draft_contract.name, vehicle)

	def test_blocks_a_second_active_lease_on_same_contract(self):
		vehicle = get_or_create_vehicle("STRIDE-TEST-LS-002")
		contract = make_rental_contract(vehicle, self.customer)
		contract.submit()

		first = make_lease(contract.name, vehicle)
		first.submit()
		self.addCleanup(lambda: frappe.db.set_value("Lease", first.name, "docstatus", 2))

		with self.assertRaises(frappe.ValidationError):
			make_lease(contract.name, vehicle)

	def test_end_date_calculated_for_daily_period(self):
		# duration/period_type/rate are fetch_from(rental_contract) read-only fields on
		# Lease, so they must be set on the contract, not overridden on the lease itself.
		vehicle = get_or_create_vehicle("STRIDE-TEST-LS-003")
		contract = make_rental_contract(vehicle, self.customer, duration=7, period_type="Daily", rate=100)
		contract.submit()

		start = today()
		lease = make_lease(contract.name, vehicle, start_date=start)

		self.assertEqual(lease.end_date, getdate(add_days(start, 7)))
		self.assertEqual(lease.total_amount, 700)

	def test_submit_generates_payment_schedule_and_marks_vehicle_rented(self):
		vehicle = get_or_create_vehicle("STRIDE-TEST-LS-004")
		contract = make_rental_contract(vehicle, self.customer, duration=3)
		contract.submit()

		lease = make_lease(contract.name, vehicle)
		lease.submit()
		self.addCleanup(lambda: frappe.db.set_value("Lease", lease.name, "docstatus", 2))

		lease.reload()
		self.assertEqual(len(lease.payment_schedule), 3)
		self.assertEqual(frappe.db.get_value("Vehicle", vehicle, "vehicle_status"), "Rented")
		self.assertEqual(frappe.db.get_value("Rental Contract", contract.name, "status"), "Active")
