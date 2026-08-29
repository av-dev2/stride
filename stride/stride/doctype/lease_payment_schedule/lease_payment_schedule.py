# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class LeasePaymentSchedule(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		due_date: DF.Date
		from_date: DF.Date
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		payment_entry: DF.Link | None
		period: DF.Int
		sales_invoice: DF.Link | None
		status: DF.Literal["Pending", "Invoiced", "Paid", "Overdue", "Postponed"]
		to_date: DF.Date
	# end: auto-generated types

	pass
