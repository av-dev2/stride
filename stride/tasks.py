# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

"""Scheduled tasks for the Stride app."""

import frappe
from frappe import _
from frappe.utils import getdate, today


def generate_lease_invoices() -> None:
	"""Daily scheduled job: create Sales Invoices for due Lease Payment Schedule rows.

	Reads the `rental_service` from the Vehicle linked to each Lease. Income account
	and cost center are derived from the Item's defaults (multi-company safe).

	Only processes rows where:
	- Lease is submitted (docstatus=1) and Active
	- Schedule row status is "Pending"
	- Schedule row due_date <= today  (scans from start of schedule, not just today)
	- No Sales Invoice is already linked

	Backfill behaviour:
	  When a Rental Contract is finalised after the schedule start date, earlier
	  periods whose due_date has already passed will still have no invoice.  This
	  function intentionally scans the **entire** schedule from period 1 so that
	  those past-due rows are caught and invoiced on the next run.
	"""
	settings = frappe.get_cached_doc("Stride Settings")

	if not settings.enable_auto_invoicing:
		return

	due_rows = _get_due_schedule_rows()

	if not due_rows:
		return

	created_count = 0
	error_count = 0

	for row in due_rows:
		try:
			_create_sales_invoice_for_row(row)
			created_count += 1
		except Exception:
			error_count += 1
			frappe.log_error(
				title=f"Auto-Invoice failed: {row.parent} Period {row.period}",
				message=frappe.get_traceback(),
			)

	if created_count:
		frappe.logger("stride").info(
			f"Auto-Invoicing: {created_count} invoices created, {error_count} errors"
		)


def _get_due_schedule_rows() -> list[dict]:
	"""Fetch Lease Payment Schedule rows that are due for invoicing.

	Scans from the **start** of every active schedule (period 1 onwards) so that
	past-due rows created before the contract was finalised are also caught and
	backfilled.  Only rows belonging to submitted, Active Leases are returned.
	"""
	# Collect IDs of submitted, Active Leases so we can scope the schedule query.
	# Using a sub-select via get_all keeps us within the Frappe ORM (no raw SQL).
	active_lease_names = frappe.db.get_all(
		"Lease",
		filters={
			"docstatus": 1,
			"status": "Active",
		},
		pluck="name",
	)

	if not active_lease_names:
		return []

	# Fetch ALL pending, un-invoiced rows whose due_date is on or before today,
	# starting from period 1 of each schedule (the query has no lower-bound date
	# filter so past periods are naturally included).
	return frappe.db.get_all(
		"Lease Payment Schedule",
		filters={
			"parenttype": "Lease",
			"parent": ("in", active_lease_names),
			"status": "Pending",
			"due_date": ("<=", today()),
			"sales_invoice": ("is", "not set"),
		},
		fields=[
			"name",
			"parent",
			"period",
			"from_date",
			"to_date",
			"due_date",
			"amount",
		],
		order_by="parent asc, due_date asc",
	)


def _create_sales_invoice_for_row(row: dict) -> None:
	"""Create and submit a Sales Invoice for a single schedule row.

	The invoice item (rental_service) is read from the Vehicle record linked to the
	Lease. This allows each vehicle type to have its own distinct service item.

	Args:
	        row: Lease Payment Schedule row dict
	"""
	lease = frappe.get_cached_doc("Lease", row.parent)

	# Read the rental service item from the linked Vehicle
	rental_service = None
	if lease.vehicle:
		rental_service = frappe.db.get_value("Vehicle", lease.vehicle, "rental_service")

	if not rental_service:
		frappe.throw(
			_(
				"Cannot create invoice: Vehicle {0} linked to Lease {1} does not have a "
				"<b>Rental Service</b> configured. "
				"Please set the Rental Service on the Vehicle record."
			).format(lease.vehicle or "(none)", lease.name)
		)

	# Get company from the linked Rental Contract
	company = frappe.db.get_value("Rental Contract", lease.rental_contract, "company")
	if not company:
		frappe.throw(
			_("Cannot create invoice: Rental Contract {0} has no company set.").format(lease.rental_contract)
		)

	si = frappe.new_doc("Sales Invoice")
	si.customer = lease.customer
	si.company = company
	si.posting_date = row.due_date or getdate(today())
	si.due_date = row.due_date
	si.set_posting_time = 1

	si.append(
		"items",
		{
			"item_code": rental_service,
			"qty": 1,
			"rate": row.amount,
			"description": _("Rental payment for Vehicle {0} - Period {1} ({2} to {3})").format(
				lease.vehicle, row.period, row.from_date, row.to_date
			),
		},
	)

	# Set Vehicle as accounting dimension if the field exists
	if lease.vehicle and hasattr(si, "vehicle"):
		si.vehicle = lease.vehicle

	si.insert(ignore_permissions=True)
	si.submit()

	# Update the schedule row with the invoice reference and status
	frappe.db.set_value(
		"Lease Payment Schedule",
		row.name,
		{"sales_invoice": si.name, "status": "Invoiced"},
	)


def poll_gps_data() -> None:
	"""Cron job (every 15 min): poll IOPGPS API for vehicle locations.

	Fetches real-time device positions and creates GPS Log records.
	Configured via Stride Settings (GPS section).
	"""
	from stride.api.gps import poll_iopgps_locations

	result = poll_iopgps_locations()

	if result.get("errors"):
		frappe.log_error(
			title="GPS Polling: Errors",
			message="\n".join(result["errors"]),
		)
