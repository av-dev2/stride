// Copyright (c) 2024, elius-dev and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Handover", {
	setup(frm) {
		// Allow any submitted contract — rent-to-own validation is enforced server-side
		// only when handover_type is "Ownership Transfer"
		frm.set_query("rental_contract", () => ({
			filters: { docstatus: 1 },
		}));

		// Only show submitted leases for the selected contract
		frm.set_query("lease", () => {
			const filters = { docstatus: 1 };
			if (frm.doc.rental_contract) {
				filters.rental_contract = frm.doc.rental_contract;
			}
			return { filters };
		});

		// Filter handover templates
		frm.set_query("contract_template", () => ({
			filters: { template_type: "Vehicle Handover" },
		}));

		// Set rental_item query based on current handover_type
		frm.trigger("set_rental_item_query");
	},

	handover_type(frm) {
		// Clear rental_item when handover type changes so the user re-selects
		frm.set_value("rental_item", "");
		frm.trigger("set_rental_item_query");
	},

	set_rental_item_query(frm) {
		// Ownership Transfer → stock item (vehicle asset transferred from inventory)
		// Rental Return     → non-stock service item (rental service charge)
		const is_ownership = frm.doc.handover_type === "Ownership Transfer";
		frm.set_query("rental_item", () => ({
			filters: {
				disabled: 0,
				is_stock_item: is_ownership ? 1 : 0,
			},
		}));
	},

	rental_contract(frm) {
		// Clear lease when contract changes
		if (!frm.doc.rental_contract) {
			frm.set_value("lease", "");
		}
	},

	contract_template(frm) {
		// Re-render template on change
		if (frm.doc.contract_template) {
			frm.dirty();
		}
	},
});
