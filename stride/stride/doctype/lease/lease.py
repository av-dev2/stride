# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, add_months, add_to_date, flt, getdate


# nosemgrep: frappe-modifying-but-not-comitting-other-method
class Lease(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from stride.stride.doctype.lease_payment_schedule.lease_payment_schedule import (
			LeasePaymentSchedule,
		)

		amended_from: DF.Link | None
		customer: DF.Link | None
		customer_name: DF.Data | None
		duration: DF.Int | None
		end_date: DF.Date | None
		payment_schedule: DF.Table[LeasePaymentSchedule]
		period_type: DF.Literal["", "Daily", "Weekly", "Monthly", "Yearly"]
		rate: DF.Currency
		rental_contract: DF.Link
		start_date: DF.Date
		status: DF.Literal["Active", "Completed", "Overdue", "Cancelled"]
		total_amount: DF.Currency
		total_outstanding: DF.Currency
		total_paid: DF.Currency
		total_periods: DF.Int | None
		vehicle: DF.Link | None
	# end: auto-generated types

	def validate(self) -> None:
		self._validate_rental_contract()
		self._calculate_end_date()
		self._calculate_totals()

	def on_submit(self) -> None:
		self._generate_payment_schedule()
		self._calculate_totals()
		self._commit_totals_to_db()
		self._set_vehicle_status("Rented")
		self._set_contract_status("Active")

	def on_cancel(self) -> None:
		self._cancel_unpaid_invoices()
		self._set_vehicle_status("Available")
		self.db_set("status", "Cancelled")

	def _validate_rental_contract(self) -> None:
		"""Ensure the linked Rental Contract is submitted."""
		if not self.rental_contract:
			return

		contract_docstatus = frappe.db.get_value("Rental Contract", self.rental_contract, "docstatus")
		if contract_docstatus != 1:
			frappe.throw(
				_("Rental Contract {0} must be submitted before creating a Lease.").format(
					self.rental_contract
				)
			)

		# Block duplicate active leases for the same contract
		existing_lease = frappe.db.exists(
			"Lease",
			{
				"rental_contract": self.rental_contract,
				"docstatus": 1,
				"name": ("!=", self.name),
			},
		)
		if existing_lease:
			frappe.throw(
				_("An active Lease {0} already exists for Rental Contract {1}.").format(
					existing_lease, self.rental_contract
				)
			)

	def _calculate_end_date(self) -> None:
		"""Auto-calculate end_date from start_date + duration + period_type."""
		if not self.start_date or not self.duration or not self.period_type:
			return

		start = getdate(self.start_date)

		if self.period_type == "Daily":
			self.end_date = add_days(start, self.duration)
		elif self.period_type == "Weekly":
			self.end_date = add_days(start, self.duration * 7)
		elif self.period_type == "Monthly":
			self.end_date = add_months(start, self.duration)
		elif self.period_type == "Yearly":
			self.end_date = add_to_date(start, years=self.duration)

		self.total_periods = self.duration
		self.total_amount = flt(self.rate) * self.duration

	def _generate_payment_schedule(self) -> None:
		"""Generate Lease Payment Schedule rows on submit."""
		self.payment_schedule = []
		if not self.start_date or not self.duration or not self.period_type:
			return

		start = getdate(self.start_date)

		for i in range(self.duration):
			from_date = self._add_periods(start, i)
			to_date = add_days(self._add_periods(start, i + 1), -1)
			due_date = from_date  # Payment due at start of each period

			self.append(
				"payment_schedule",
				{
					"period": i + 1,
					"from_date": from_date,
					"to_date": to_date,
					"due_date": due_date,
					"amount": self.rate,
					"status": "Pending",
				},
			)

		# Save the child rows to DB since we're in on_submit
		for row in self.payment_schedule:
			row.db_insert()

	def _add_periods(self, start_date: str, periods: int):
		"""Add N periods to start_date based on period_type."""
		if self.period_type == "Daily":
			return add_days(start_date, periods)
		elif self.period_type == "Weekly":
			return add_days(start_date, periods * 7)
		elif self.period_type == "Monthly":
			return add_months(start_date, periods)
		elif self.period_type == "Yearly":
			return add_to_date(start_date, years=periods)
		return start_date

	def _calculate_totals(self) -> None:
		"""Recalculate payment summary from schedule rows."""
		self.total_periods = self.duration or 0
		self.total_amount = flt(self.rate) * (self.duration or 0)

		paid = 0.0
		for row in self.payment_schedule:
			if row.status == "Paid":
				paid += flt(row.amount)

		self.total_paid = paid
		self.total_outstanding = flt(self.total_amount) - paid

	def _commit_totals_to_db(self) -> None:
		"""Persist computed totals to DB (required in on_submit context)."""
		self.db_set(
			{
				"total_periods": self.total_periods,
				"total_amount": self.total_amount,
				"total_paid": self.total_paid,
				"total_outstanding": self.total_outstanding,
			},
			update_modified=False,
		)

	def _set_vehicle_status(self, status: str) -> None:
		"""Update the vehicle_status custom field on the Vehicle."""
		if self.vehicle:
			frappe.db.set_value("Vehicle", self.vehicle, "vehicle_status", status)

	def _set_contract_status(self, status: str) -> None:
		"""Update the status on the linked Rental Contract."""
		if self.rental_contract:
			frappe.db.set_value("Rental Contract", self.rental_contract, "status", status)

	def _cancel_unpaid_invoices(self) -> None:
		"""Cancel Sales Invoices linked to unpaid / postponed schedule rows."""
		for row in self.payment_schedule:
			if row.sales_invoice and row.status in ("Pending", "Invoiced", "Overdue", "Postponed"):
				try:
					si = frappe.get_doc("Sales Invoice", row.sales_invoice)
					if si.docstatus == 1:
						si.cancel()
					row.db_set("sales_invoice", None)
					row.db_set("status", "Pending")
				except Exception:
					frappe.log_error(
						title=f"Lease cancel: failed to cancel SI {row.sales_invoice}",
						message=frappe.get_traceback(),
					)


@frappe.whitelist()
def postpone_schedule_row(schedule_row_name: str) -> dict:
	"""Postpone a Lease Payment Schedule row.

	If a Sales Invoice is already linked:
	- Cancels it if it is NOT in paid status (outstanding_amount > 0).
	- Leaves it untouched if it has been fully paid.

	Sets the row status to 'Postponed' in both cases (the invoice link is
	cleared only when the invoice is cancelled).

	Args:
		schedule_row_name: The `name` of the Lease Payment Schedule child row.

	Returns:
		dict with keys `cancelled_invoice` (str|None) and `message` (str).
	"""
	row = frappe.get_doc("Lease Payment Schedule", schedule_row_name)

	if row.status == "Paid":
		frappe.throw(_("Cannot postpone a schedule row that has already been paid."))

	cancelled_invoice = None

	if row.sales_invoice:
		si = frappe.get_doc("Sales Invoice", row.sales_invoice)

		if flt(si.outstanding_amount) <= 0:
			frappe.throw(_("Cannot postpone a schedule row that has already been paid."))

		if si.docstatus == 1:
			si.cancel()

		cancelled_invoice = si.name
		row.db_set("sales_invoice", None)

		if si.docstatus != 1:
			si.delete()

	row.db_set("status", "Postponed")

	return {
		"cancelled_invoice": cancelled_invoice,
		"message": _("Period {0} has been postponed.{1}").format(
			row.period,
			(" " + _("Invoice {0} was cancelled.").format(cancelled_invoice)) if cancelled_invoice else "",
		),
	}
