# Copyright (c) 2026, elius-dev and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import now_datetime


class TestPaymentLog(IntegrationTestCase):
	def test_can_insert_with_its_declared_fields(self):
		doc = frappe.get_doc(
			{
				"doctype": "Payment Log",
				"posting_date": now_datetime().date(),
				"posting_time": now_datetime().time(),
				"paid_amount": 150.0,
				"payment_method": "Cash",
				"paid_to": "Test Cash Account",
				"description": "Test payment log entry",
			}
		)
		doc.insert(ignore_permissions=True)
		self.addCleanup(lambda: frappe.delete_doc("Payment Log", doc.name, ignore_permissions=True))

		doc.reload()
		self.assertEqual(doc.paid_amount, 150.0)
		self.assertFalse(doc.reconciled)
