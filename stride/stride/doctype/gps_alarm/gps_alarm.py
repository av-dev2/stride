# Copyright (c) 2026, elius-dev and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class GPSAlarm(Document):
	"""One alarm event reported by a tracking device."""

	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		address: DF.SmallText | None
		alarm_code: DF.Data
		alarm_description: DF.SmallText | None
		alarm_time: DF.Datetime
		archive_url: DF.Data | None
		battery_capacity: DF.Float
		gps_tracker: DF.Link | None
		heading: DF.Float
		image_urls: DF.SmallText | None
		latitude: DF.Float
		longitude: DF.Float
		position_type: DF.Data | None
		speed: DF.Float
		vehicle: DF.Link
		video_url: DF.Data | None
	# end: auto-generated types


def on_doctype_update():
	frappe.db.add_unique(
		"GPS Alarm", ["gps_tracker", "alarm_time", "alarm_code"], constraint_name="unique_gps_alarm"
	)
	frappe.db.add_index("GPS Alarm", ["vehicle", "alarm_time"])
