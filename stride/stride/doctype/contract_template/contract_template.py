# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ContractTemplate(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		content: DF.TextEditor
		is_default: DF.Check
		template_name: DF.Data
		template_type: DF.Literal["Renting Agreement", "Vehicle Handover"]
	# end: auto-generated types

	def validate(self) -> None:
		if self.is_default:
			self._clear_other_defaults()

	def _clear_other_defaults(self) -> None:
		"""Ensure only one template per type is marked as default."""
		frappe.db.set_value(
			"Contract Template",
			{
				"is_default": 1,
				"template_type": self.template_type,
				"name": ("!=", self.name),
			},
			"is_default",
			0,
		)
