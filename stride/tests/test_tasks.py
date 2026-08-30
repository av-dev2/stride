# Copyright (c) 2026, elius-dev and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

from stride.tasks import _apply_item_tax_template
from stride.tests.utils import get_default_test_company, get_or_create_rental_service_item


def ensure_item_default_tax_template_field() -> None:
	"""Simulate the csf_tz custom field this fix depends on, without installing csf_tz."""
	if frappe.get_meta("Item").has_field("default_tax_template"):
		return

	frappe.get_doc(
		{
			"doctype": "Custom Field",
			"dt": "Item",
			"fieldname": "default_tax_template",
			"label": "Default Tax Template",
			"fieldtype": "Link",
			"options": "Item Tax Template",
			"insert_after": "item_group",
		}
	).insert(ignore_permissions=True)
	frappe.clear_cache(doctype="Item")


def make_item_tax_template(title: str, company: str, tax_rate: float = 0) -> str:
	existing = frappe.db.get_value("Item Tax Template", {"title": title, "company": company}, "name")
	if existing:
		return existing

	account = frappe.db.get_value(
		"Account",
		{"company": company, "account_type": "Chargeable", "is_group": 0},
		"name",
	)
	doc = frappe.get_doc(
		{
			"doctype": "Item Tax Template",
			"title": title,
			"company": company,
			"taxes": [{"tax_type": account, "tax_rate": tax_rate}],
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


class TestApplyItemTaxTemplate(IntegrationTestCase):
	def test_no_op_when_item_has_no_default_tax_template(self):
		si = frappe.new_doc("Sales Invoice")
		item_row = si.append("items", {"item_code": "x", "qty": 1, "rate": 100})

		_apply_item_tax_template(si, item_row, get_or_create_rental_service_item(), "Some Company")

		self.assertEqual(len(si.taxes), 0)
		self.assertFalse(item_row.item_tax_template)

	def test_adds_tax_row_from_item_default_tax_template(self):
		ensure_item_default_tax_template_field()
		company = get_default_test_company()
		item_code = get_or_create_rental_service_item("Stride Test Rental Service Taxed")
		template = make_item_tax_template("Stride Test Exempt VAT", company, tax_rate=0)
		frappe.db.set_value("Item", item_code, "default_tax_template", template)

		si = frappe.new_doc("Sales Invoice")
		si.company = company
		item_row = si.append("items", {"item_code": item_code, "qty": 1, "rate": 25000})

		_apply_item_tax_template(si, item_row, item_code, company)

		self.assertEqual(item_row.item_tax_template, template)
		self.assertEqual(len(si.taxes), 1)
		self.assertEqual(si.taxes[0].charge_type, "On Net Total")
		self.assertEqual(si.taxes[0].rate, 0)
