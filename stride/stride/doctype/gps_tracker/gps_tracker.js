// Copyright (c) 2026, elius-dev and contributors
// For license information, please see license.txt

frappe.ui.form.on("GPS Tracker", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		frm.add_custom_button(
			__("Live Location"),
			() => stride_show_live_location(frm),
			__("Device")
		);
		frm.add_custom_button(
			__("Device Details"),
			() => stride_show_device_detail(frm),
			__("Device")
		);
		frm.add_custom_button(
			__("Mileage"),
			() => stride_prompt_mileage(frm),
			__("Device")
		);
		frm.add_custom_button(
			__("Pull Alarms"),
			() => stride_prompt_pull_alarms(frm),
			__("Device")
		);

		if (frm.doc.vehicle) {
			frm.add_custom_button(__("Open Map"), () => {
				frappe.set_route("vehicle-map", { vehicle: frm.doc.vehicle });
			});
		}
	},
});

function stride_show_live_location(frm) {
	frm
		.call({
			method: "stride.api.gps.get_live_location",
			args: { tracker: frm.doc.name },
			freeze: true,
			freeze_message: __("Asking the device..."),
		})
		.then((r) => {
			const data = r.message || {};

			if (!data.latitude) {
				frappe.msgprint(
					__("The provider returned no position for this device.")
				);
				return;
			}

			frappe.msgprint({
				title: __("Live Location"),
				message: `
				<p>${frappe.utils.escape_html(data.address || __("Address unavailable"))}</p>
				<p class="text-muted">${data.latitude}, ${data.longitude}</p>
				<a href="https://www.openstreetmap.org/?mlat=${data.latitude}&mlon=${
					data.longitude
				}#map=17/${data.latitude}/${data.longitude}"
				   target="_blank" rel="noopener">${__("Open in OpenStreetMap")}</a>
			`,
			});
		});
}

function stride_show_device_detail(frm) {
	frm
		.call({
			method: "stride.api.gps.get_device_detail",
			args: { tracker: frm.doc.name },
			freeze: true,
		})
		.then((r) => {
			const data = r.message || {};
			const brief = data.deviceBrief || {};
			const status = data.deviceStatus || {};

			frappe.msgprint({
				title: __("Device Details"),
				message: stride_definition_list([
					[__("Name"), brief.name],
					[__("Type"), brief.deviceType],
					[__("SIM"), brief.deviceMobile],
					[__("Status"), status.status],
					[__("Today's Mileage"), status.todayMile],
					[__("Total Mileage"), status.totalMile],
					[__("Battery"), status.batteryPercentage],
					[__("Voltage"), status.externalVoltage],
				]),
			});
		});
}

function stride_prompt_mileage(frm) {
	stride_prompt_date_range(__("Mileage"), (values) => {
		frm
			.call({
				method: "stride.api.gps.get_mileage",
				args: {
					tracker: frm.doc.name,
					from_datetime: values.from_datetime,
					to_datetime: values.to_datetime,
				},
				freeze: true,
			})
			.then((r) => {
				const data = r.message || {};
				frappe.msgprint({
					title: __("Mileage"),
					message: stride_definition_list([
						[__("Distance"), `${flt(data.miles, 1)} km`],
						[__("Running Time"), `${flt(data.run_time / 3600, 1)} h`],
					]),
				});
			});
	});
}

function stride_prompt_pull_alarms(frm) {
	stride_prompt_date_range(__("Pull Alarms"), (values) => {
		frm
			.call({
				method: "stride.api.gps.pull_alarms",
				args: {
					tracker: frm.doc.name,
					from_datetime: values.from_datetime,
					to_datetime: values.to_datetime,
				},
				freeze: true,
				freeze_message: __("Fetching alarms..."),
			})
			.then((r) => {
				const data = r.message || {};
				frappe.show_alert({
					message: __("{0} of {1} alarms stored.", [
						data.created,
						data.fetched,
					]),
					indicator: data.created ? "green" : "blue",
				});
			});
	});
}

function stride_prompt_date_range(title, callback) {
	frappe.prompt(
		[
			{
				fieldname: "from_datetime",
				fieldtype: "Datetime",
				label: __("From"),
				reqd: 1,
				default: stride_days_ago(7),
			},
			{
				fieldname: "to_datetime",
				fieldtype: "Datetime",
				label: __("To"),
				reqd: 1,
				default: frappe.datetime.now_datetime(),
			},
		],
		callback,
		title,
		__("Fetch")
	);
}

// frappe.datetime.add_days returns ISO-8601 with an offset, which a Datetime
// control cannot parse. Build the value in the format now_datetime() returns.
function stride_days_ago(days) {
	return moment().subtract(days, "days").format(frappe.defaultDatetimeFormat);
}

function stride_definition_list(rows) {
	return rows
		.filter(
			([, value]) => value !== undefined && value !== null && value !== ""
		)
		.map(
			([label, value]) =>
				`<div class="flex justify-between" style="padding: 4px 0;">
					<span class="text-muted">${label}</span>
					<strong>${frappe.utils.escape_html(String(value))}</strong>
				</div>`
		)
		.join("");
}
