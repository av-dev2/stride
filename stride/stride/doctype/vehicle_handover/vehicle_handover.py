# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class VehicleHandover(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		contract_template: DF.Link | None
		customer: DF.Link | None
		customer_name: DF.Data | None
		guarantor_id_no: DF.Data | None
		guarantor_name: DF.Data | None
		handover_attachment: DF.Attach | None
		handover_content: DF.TextEditor | None
		handover_date: DF.Date
		handover_type: DF.Literal["Rental Return", "Ownership Transfer"]
		inspection_notes: DF.SmallText | None
		lease: DF.Link
		naming_series: DF.Literal["VH-.#####"]
		odometer_reading: DF.Float | None
		rental_contract: DF.Link
		rental_item: DF.Link
		vehicle: DF.Link | None
		vehicle_condition: DF.Literal["Excellent", "Good", "Fair", "Poor"]
	# end: auto-generated types

	def validate(self) -> None:
		self._validate_ownership_transfer_contract()
		self._validate_all_payments_paid()
		self._render_handover_template()

	def on_submit(self) -> None:
		if self.handover_type == "Ownership Transfer":
			self._create_stock_entry()
			self._set_vehicle_status("Owned by Client")
		else:
			self._set_vehicle_status("Available")
		self._set_contract_status("Completed")
		self._set_lease_status("Completed")

	def on_cancel(self) -> None:
		if self.handover_type == "Ownership Transfer":
			self._reverse_stock_entry()
			self._set_vehicle_status("Rented")
		else:
			self._set_vehicle_status("Rented")
		self._set_contract_status("Active")
		self._set_lease_status("Active")

	def _validate_ownership_transfer_contract(self) -> None:
		"""For Ownership Transfer handovers, block if the contract is not rent-to-own."""
		if self.handover_type != "Ownership Transfer":
			return

		rent_to_own = frappe.db.get_value("Rental Contract", self.rental_contract, "rent_to_own")
		if not rent_to_own:
			frappe.throw(
				_(
					"Ownership Transfer handover can only be created for "
					"<b>Rent to Own</b> contracts. "
					"Contract {0} is a standard rental."
				).format(self.rental_contract)
			)

	def _validate_all_payments_paid(self) -> None:
		"""Verify all Lease Payment Schedule rows are Paid."""
		unpaid_count = frappe.db.count(
			"Lease Payment Schedule",
			filters={
				"parent": self.lease,
				"parenttype": "Lease",
				"status": ("!=", "Paid"),
			},
		)
		if unpaid_count:
			frappe.throw(
				_(
					"All payments must be completed before vehicle handover. "
					"Lease {0} has <b>{1}</b> unpaid period(s)."
				).format(self.lease, unpaid_count)
			)

	def _render_handover_template(self) -> None:
		"""Render Jinja content from the selected Contract Template."""
		if not self.contract_template:
			return

		template_content = frappe.db.get_value("Contract Template", self.contract_template, "content")
		if not template_content:
			return

		context = self._get_template_context()
		try:
			# nosemgrep: frappe-ssti -- template_content from Contract Template DocType (trusted)
			self.handover_content = frappe.render_template(template_content, context)
		except Exception:
			frappe.log_error(
				title=f"Handover template render failed - {self.name}",
				message=frappe.get_traceback(),
			)
			frappe.msgprint(
				_("Failed to render handover template. " "Please check the template for errors."),
				indicator="orange",
			)

	def _get_template_context(self) -> dict:
		"""Build the Jinja context for handover template rendering."""
		return {
			"customer": self.customer,
			"customer_name": self.customer_name,
			"vehicle": self.vehicle,
			"handover_date": self.handover_date,
			"handover_type": self.handover_type,
			"vehicle_condition": self.vehicle_condition,
			"odometer_reading": self.odometer_reading,
			"inspection_notes": self.inspection_notes,
			"guarantor_name": self.guarantor_name,
			"guarantor_id_no": self.guarantor_id_no,
			"rental_contract": self.rental_contract,
			"lease": self.lease,
		}

	def _create_stock_entry(self) -> None:
		"""Create a Material Issue Stock Entry to remove vehicle from inventory (Ownership Transfer only)."""
		vehicle_doc = frappe.get_doc("Vehicle", self.vehicle)
		item_code = self.rental_item or vehicle_doc.get("item_code")
		warehouse = vehicle_doc.get("warehouse")

		if not item_code or not warehouse:
			frappe.msgprint(
				_(
					"Vehicle {0} does not have Item Code or Warehouse configured. " "Skipping stock entry."
				).format(self.vehicle),
				indicator="orange",
			)
			return

		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Issue"
		se.posting_date = self.handover_date
		se.remarks = _("Vehicle handover to {0} via {1}").format(self.customer_name, self.name)

		se.append(
			"items",
			{
				"item_code": item_code,
				"s_warehouse": warehouse,
				"qty": 1,
			},
		)

		se.insert(ignore_permissions=True)
		se.submit()

		frappe.msgprint(
			_("Stock Entry {0} created for vehicle ownership transfer.").format(se.name),
			indicator="green",
		)

	def _reverse_stock_entry(self) -> None:
		"""Find and cancel the Stock Entry created during submit."""
		stock_entries = frappe.get_all(
			"Stock Entry",
			filters={
				"stock_entry_type": "Material Issue",
				"remarks": ("like", f"%{self.name}%"),
				"docstatus": 1,
			},
			pluck="name",
		)

		for se_name in stock_entries:
			try:
				se = frappe.get_doc("Stock Entry", se_name)
				se.cancel()
				frappe.msgprint(
					_("Stock Entry {0} cancelled.").format(se_name),
					indicator="blue",
				)
			except Exception:
				frappe.log_error(
					title=f"Handover cancel: failed to cancel SE {se_name}",
					message=frappe.get_traceback(),
				)

	def _set_vehicle_status(self, status: str) -> None:
		"""Update vehicle_status custom field on Vehicle."""
		if self.vehicle:
			frappe.db.set_value("Vehicle", self.vehicle, "vehicle_status", status)

	def _set_contract_status(self, status: str) -> None:
		"""Update status on Rental Contract."""
		if self.rental_contract:
			frappe.db.set_value("Rental Contract", self.rental_contract, "status", status)

	def _set_lease_status(self, status: str) -> None:
		"""Update status on Lease."""
		if self.lease:
			frappe.db.set_value("Lease", self.lease, "status", status)
