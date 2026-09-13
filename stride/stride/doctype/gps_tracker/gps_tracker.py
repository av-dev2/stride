# Copyright (c) 2026, elius-dev and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class GPSTracker(Document):
	"""One physical tracking device, bound to a provider account and a vehicle."""

	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		device_type: DF.Data | None
		gps_provider: DF.Link
		imei: DF.Data
		is_active: DF.Check
		last_seen_on: DF.Datetime | None
		last_status: DF.Data | None
		sim_number: DF.Data | None
		tracker_name: DF.Data | None
		vehicle: DF.Link | None
	# end: auto-generated types

	def validate(self) -> None:
		self.imei = (self.imei or "").strip()

		if not self.tracker_name:
			self.tracker_name = self.imei

	def get_client(self):
		"""Return an API client for the provider this tracker belongs to."""
		return frappe.get_doc("GPS Provider", self.gps_provider).get_client()
