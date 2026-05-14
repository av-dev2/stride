// Copyright (c) 2024, elius-dev and contributors
// For license information, please see license.txt

frappe.ui.form.on("Lease", {
	setup(frm) {
		// Only show submitted Rental Contracts
		frm.set_query("rental_contract", () => ({
			filters: { docstatus: 1 },
		}));
	},

	refresh(frm) {
		frm.trigger("set_status_indicator");
	},

	set_status_indicator(frm) {
		if (frm.doc.docstatus === 0) return;

		const colors = {
			Active: "blue",
			Completed: "green",
			Overdue: "red",
			Cancelled: "grey",
		};

		const color = colors[frm.doc.status] || "grey";
		frm.page.set_indicator(frm.doc.status, color);
	},
});
