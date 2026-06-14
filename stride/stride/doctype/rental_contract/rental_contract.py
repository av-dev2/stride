# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today


class RentalContract(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        amended_from: DF.Link | None
        company: DF.Link | None
        contract_attachment: DF.Attach | None
        contract_content: DF.TextEditor | None
        contract_template: DF.Link | None
        customer: DF.Link
        customer_contact: DF.Data | None
        customer_identification_no: DF.Data
        customer_identification_type: DF.Literal[
            "National ID", "TIN", "Driver License", "Passport", "Voter ID"
        ]
        customer_name: DF.Data | None
        duration: DF.Int
        guarantor_contact: DF.Data | None
        guarantor_id_no: DF.Data
        guarantor_name: DF.Data
        naming_series: DF.Literal["RC-.#####"]
        period_type: DF.Literal["Daily", "Weekly", "Monthly", "Yearly"]
        rate: DF.Currency
        rent_to_own: DF.Check
        status: DF.Literal["Draft", "Active", "Completed", "Cancelled"]
        total_amount: DF.Currency
        vehicle: DF.Link
        vehicle_name: DF.Data | None
    # end: auto-generated types

    def validate(self) -> None:
        self._calculate_total_amount()
        self._validate_vehicle_availability()
        self._render_contract_template()

    def on_submit(self) -> None:
        # Status stays Draft until a Lease is created and submitted
        self.db_set("status", "Draft")

    def on_cancel(self) -> None:
        self._block_if_active_lease()
        self.db_set("status", "Cancelled")

    def _calculate_total_amount(self) -> None:
        """total_amount = rate * duration (number of periods)."""
        self.total_amount = (self.rate or 0) * (self.duration or 0)

    def _validate_vehicle_availability(self) -> None:
        """Ensure the selected vehicle is available for rental."""
        if self.is_new() or self.has_value_changed("vehicle"):
            vehicle_status = frappe.db.get_value("Vehicle", self.vehicle, "vehicle_status")
            if vehicle_status and vehicle_status != "Available":
                frappe.throw(
                    _(
                        "Vehicle {0} is currently <b>{1}</b>. "
                        "Only vehicles with status <b>Available</b> can be rented."
                    ).format(self.vehicle, vehicle_status)
                )

    def _render_contract_template(self) -> None:
        """Render Jinja content from the selected Contract Template."""
        if not self.contract_template:
            return

        template_content = frappe.db.get_value("Contract Template", self.contract_template, "content")
        if not template_content:
            return

        context = self._get_template_context()
        try:
            # nosemgrep: frappe-ssti -- template_content from Contract Template DocType (trusted)
            self.contract_content = frappe.render_template(template_content, context)
        except Exception:
            frappe.log_error(
                title=f"Contract template render failed - {self.name}",
                message=frappe.get_traceback(),
            )
            frappe.msgprint(
                _("Failed to render contract template. " "Please check the template for errors."),
                indicator="orange",
            )

    def _get_template_context(self) -> dict:
        """Build the Jinja context dictionary for template rendering."""
        return {
            "customer": self.customer,
            "customer_name": self.customer_name,
            "customer_contact": self.customer_contact,
            "customer_identification_type": self.customer_identification_type,
            "customer_identification_no": self.customer_identification_no,
            "guarantor_name": self.guarantor_name,
            "guarantor_id_no": self.guarantor_id_no,
            "guarantor_contact": self.guarantor_contact,
            "vehicle": self.vehicle,
            "vehicle_name": self.vehicle_name,
            "rate": frappe.format_value(self.rate, {"fieldtype": "Currency"}),
            "period_type": self.period_type,
            "duration": self.duration,
            "total_amount": frappe.format_value(self.total_amount, {"fieldtype": "Currency"}),
            "rent_to_own": self.rent_to_own,
            "company": self.company or frappe.defaults.get_defaults().get("company"),
            "today": today(),
            # Placeholders for Lease dates (filled when lease is created)
            "start_date": "",
            "end_date": "",
        }

    def _block_if_active_lease(self) -> None:
        """Prevent cancellation if an active (submitted) Lease exists."""
        active_lease = frappe.db.exists(
            "Lease",
            {"rental_contract": self.name, "docstatus": 1},
        )
        if active_lease:
            frappe.throw(
                _(
                    "Cannot cancel this Rental Contract because it has an active "
                    "Lease <b>{0}</b>. Cancel the Lease first."
                ).format(active_lease)
            )
