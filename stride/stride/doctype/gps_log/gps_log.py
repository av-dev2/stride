# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class GPSLog(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        address: DF.SmallText | None
        alert_message: DF.SmallText | None
        alert_type: DF.Data | None
        heading: DF.Float | None
        latitude: DF.Float | None
        longitude: DF.Float | None
        speed: DF.Float | None
        timestamp: DF.Datetime
        vehicle: DF.Link
    # end: auto-generated types

    pass
