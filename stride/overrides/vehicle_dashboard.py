# Copyright (c) 2024, elius-dev and contributors
# For license information, please see license.txt

"""Vehicle dashboard override for Stride."""


def get_data(data: dict | None = None) -> dict:
	"""Extend the Vehicle dashboard with Stride transactions.

	Adds Rental Contracts, Leases, Vehicle Handovers, and GPS Logs
	to the Vehicle form dashboard.
	"""
	data = data or {}

	# Ensure transactions list exists
	transactions = data.get("transactions", [])

	transactions.extend(
		[
			{"label": "Rentals", "items": ["Rental Contract", "Lease"]},
			{"label": "Operations", "items": ["Vehicle Handover", "GPS Log"]},
		]
	)

	data["transactions"] = transactions

	# All Stride DocTypes use 'vehicle' as the fieldname linking to Vehicle
	non_standard = data.get("non_standard_fieldnames", {})
	non_standard.update(
		{
			"Rental Contract": "vehicle",
			"Lease": "vehicle",
			"Vehicle Handover": "vehicle",
			"GPS Log": "vehicle",
		}
	)
	data["non_standard_fieldnames"] = non_standard

	return data
