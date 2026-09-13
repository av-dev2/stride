# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class GPSLog(Document):
	"""One position sample reported by a tracking device."""

	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		acc_status: DF.Check
		address: DF.SmallText | None
		battery_percentage: DF.Float
		device_status: DF.Data | None
		gps_tracker: DF.Link | None
		heading: DF.Float
		latitude: DF.Float
		longitude: DF.Float
		position_type: DF.Data | None
		speed: DF.Float
		timestamp: DF.Datetime
		vehicle: DF.Link
	# end: auto-generated types

	pass


def on_doctype_update():
	# The unique key is what actually stops two workers storing the same reading;
	# the ingestion check ahead of it is not atomic. The composite serves the map,
	# which asks for the newest row per vehicle.
	frappe.db.add_unique("GPS Log", ["gps_tracker", "timestamp"], constraint_name="unique_gps_reading")
	frappe.db.add_index("GPS Log", ["vehicle", "timestamp"])
