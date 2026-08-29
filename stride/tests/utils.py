"""Shared fixture builders for Stride's test suite."""

import frappe


def get_or_create_customer_group(name: str) -> str:
	if frappe.db.exists("Customer Group", name):
		return name

	parent = frappe.db.get_value("Customer Group", {"is_group": 1}, "name") or "All Customer Groups"
	if not frappe.db.exists("Customer Group", parent):
		frappe.get_doc({"doctype": "Customer Group", "customer_group_name": parent, "is_group": 1}).insert(
			ignore_permissions=True
		)

	frappe.get_doc(
		{
			"doctype": "Customer Group",
			"customer_group_name": name,
			"parent_customer_group": parent,
			"is_group": 0,
		}
	).insert(ignore_permissions=True)
	return name


def get_or_create_territory(name: str) -> str:
	if frappe.db.exists("Territory", name):
		return name

	parent = frappe.db.get_value("Territory", {"is_group": 1}, "name") or "All Territories"
	if not frappe.db.exists("Territory", parent):
		frappe.get_doc({"doctype": "Territory", "territory_name": parent, "is_group": 1}).insert(
			ignore_permissions=True
		)

	frappe.get_doc(
		{"doctype": "Territory", "territory_name": name, "parent_territory": parent, "is_group": 0}
	).insert(ignore_permissions=True)
	return name


def get_or_create_customer(customer_name: str) -> str:
	existing = frappe.db.get_value("Customer", {"customer_name": customer_name}, "name")
	if existing:
		return existing

	customer = frappe.new_doc("Customer")
	customer.customer_name = customer_name
	customer.customer_group = get_or_create_customer_group("Stride Test Group")
	customer.territory = get_or_create_territory("Stride Test Territory")
	customer.insert(ignore_permissions=True)
	return customer.name


def get_or_create_vehicle(license_plate: str, status: str = "Available") -> str:
	if frappe.db.exists("Vehicle", license_plate):
		frappe.db.set_value("Vehicle", license_plate, "vehicle_status", status)
		return license_plate

	vehicle = frappe.new_doc("Vehicle")
	vehicle.license_plate = license_plate
	vehicle.make = "Toyota"
	vehicle.model = "Hiace"
	vehicle.last_odometer = 0
	vehicle.fuel_type = "Petrol"
	vehicle.uom = "Nos"
	vehicle.vehicle_status = status
	vehicle.insert(ignore_permissions=True)
	return vehicle.name


def make_rental_contract(vehicle: str, customer: str, **overrides):
	contract = frappe.new_doc("Rental Contract")
	contract.customer = customer
	contract.customer_name = customer
	contract.customer_identification_type = "National ID"
	contract.customer_identification_no = "ID-0001"
	contract.guarantor_name = "Test Guarantor"
	contract.guarantor_id_no = "ID-0002"
	contract.vehicle = vehicle
	contract.rate = 100
	contract.period_type = "Daily"
	contract.duration = 10
	contract.update(overrides)
	contract.insert(ignore_permissions=True)
	return contract
