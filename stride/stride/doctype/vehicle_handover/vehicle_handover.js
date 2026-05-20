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
