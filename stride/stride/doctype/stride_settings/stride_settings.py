# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class StrideSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		enable_auto_reconciliation: DF.Check
		enable_auto_invoicing: DF.Check
		gps_account: DF.Data | None
		gps_api_key: DF.Password
		gps_api_url: DF.Data | None
		gps_polling_interval_minutes: DF.Int
	# end: auto-generated types

	pass
