// Copyright (c) 2024, elius-dev and contributors
// For license information, please see license.txt

frappe.ui.form.on("Rental Contract", {
	setup(frm) {
		// Filter vehicles to show only Available ones
		frm.set_query("vehicle", () => ({
			filters: { vehicle_status: "Available" },
		}));

		// Filter contract templates to Renting Agreement type
		frm.set_query("contract_template", () => ({
			filters: { template_type: "Renting Agreement" },
		}));
	},

	refresh(frm) {
		frm.trigger("set_status_indicator");
	},

	rate(frm) {
		frm.trigger("calculate_total");
	},

	duration(frm) {
		frm.trigger("calculate_total");
	},

	calculate_total(frm) {
		const total = (frm.doc.rate || 0) * (frm.doc.duration || 0);
		frm.set_value("total_amount", total);
	},

	contract_template(frm) {
		// Re-render template content on template change
		if (frm.doc.contract_template) {
			frm.dirty();
		}
	},

	set_status_indicator(frm) {
		if (frm.doc.docstatus === 0) return;

		const colors = {
			Draft: "orange",
			Active: "blue",
			Completed: "green",
			Cancelled: "red",
		};

		const color = colors[frm.doc.status] || "grey";
		frm.page.set_indicator(frm.doc.status, color);
	},
});
