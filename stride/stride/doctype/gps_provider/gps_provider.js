// Copyright (c) 2026, elius-dev and contributors
// For license information, please see license.txt

frappe.ui.form.on("GPS Provider", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		stride_show_token_status(frm);

		frm.add_custom_button(__("Test Connection"), () => {
			frm
				.call({
					method:
						"stride.stride.doctype.gps_provider.gps_provider.test_connection",
					args: { provider: frm.doc.name },
					freeze: true,
					freeze_message: __("Authenticating..."),
				})
				.then((r) => {
					if (!r.message) return;
					frappe.show_alert({
						message: __("Connected. Token valid until {0}.", [
							frappe.datetime.str_to_user(r.message.token_expires_on),
						]),
						indicator: "green",
					});
					frm.reload_doc();
				});
		});

		frm.add_custom_button(__("Poll Now"), () => {
			frm
				.call({
					method: "stride.api.gps.poll_now",
					args: { provider: frm.doc.name },
					freeze: true,
					freeze_message: __("Fetching positions..."),
				})
				.then((r) => {
					if (!r.message) return;
					frappe.msgprint({
						title: __("Polling Complete"),
						message: __("{0} new positions stored, {1} readings skipped.", [
							r.message.created,
							r.message.skipped,
						]),
						indicator: "green",
					});
					frm.reload_doc();
				});
		});

		frm.add_custom_button(__("GPS Trackers"), () => {
			frappe.set_route("List", "GPS Tracker", { gps_provider: frm.doc.name });
		});
	},
});

function stride_show_token_status(frm) {
	frm.dashboard.clear_headline();

	if (!frm.doc.token_expires_on) {
		frm.dashboard.set_headline(
			__("No access token yet. Use Test Connection to authenticate."),
			"orange"
		);
		return;
	}

	const expired = frappe.datetime.now_datetime() > frm.doc.token_expires_on;

	frm.dashboard.set_headline(
		expired
			? __("Access token expired. It is renewed on the next request.")
			: __("Access token valid until {0}.", [
					frappe.datetime.str_to_user(frm.doc.token_expires_on),
			  ]),
		expired ? "orange" : "green"
	);
}
