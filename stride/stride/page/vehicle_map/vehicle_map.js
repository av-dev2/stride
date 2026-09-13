// Copyright (c) 2024, elius-dev and contributors
// For license information, please see license.txt

const STRIDE_MAP_COLORS = {
	moving: "#16a34a",
	idle: "#2563eb",
	alarm: "#dc2626",
	route: "#7c3aed",
};

const STRIDE_MOVING_SPEED_KMH = 2;
const STRIDE_REFRESH_MS = 30000;
const STRIDE_DEFAULT_CENTER = [-6.7924, 39.2083];

frappe.pages["vehicle-map"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Vehicle Map"),
		single_column: true,
	});

	frappe.breadcrumbs.add("Stride");

	frappe.require(
		[
			"https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
			"https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
		],
		() => {
			wrapper.vehicle_map = new StrideVehicleMap(wrapper);
		}
	);
};

frappe.pages["vehicle-map"].on_page_show = function (wrapper) {
	wrapper.vehicle_map?.resume();
};

frappe.pages["vehicle-map"].on_page_hide = function (wrapper) {
	wrapper.vehicle_map?.stop_auto_refresh();
};

class StrideVehicleMap {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.page = wrapper.page;
		this.markers = {};
		this.selected_vehicle = null;
		this.refresh_interval = null;

		this.setup_page();
		// Leaflet measures the container on creation, so let the page lay out first.
		setTimeout(() => {
			this.setup_map();
			this.load_vehicles();
			this.start_auto_refresh();
		}, 100);
	}

	// ----------------------------------------------------------------
	// Layout
	// ----------------------------------------------------------------

	setup_page() {
		this.page.set_primary_action(
			__("Refresh"),
			() => this.load_vehicles(),
			"refresh"
		);

		this.vehicle_field = this.page.add_field({
			fieldtype: "Link",
			fieldname: "vehicle",
			options: "Vehicle",
			label: __("Vehicle"),
			change: () => this.on_vehicle_change(),
		});

		this.auto_refresh_field = this.page.add_field({
			fieldtype: "Check",
			fieldname: "auto_refresh",
			label: __("Auto Refresh"),
			default: 1,
			change: () => {
				if (this.auto_refresh_field.get_value()) {
					this.start_auto_refresh();
				} else {
					this.stop_auto_refresh();
				}
			},
		});

		this.route_button = this.page.add_button(__("Show Route"), () =>
			this.prompt_route()
		);
		this.route_button.prop("disabled", true);

		this.map_wrapper = $(`
			<div class="stride-map-container">
				<div id="stride-vehicle-map"></div>
				<div class="stride-map-legend">
					<span><i class="stride-dot" style="background:${
						STRIDE_MAP_COLORS.moving
					}"></i>${__("Moving")}</span>
					<span><i class="stride-dot" style="background:${
						STRIDE_MAP_COLORS.idle
					}"></i>${__("Idle")}</span>
					<span><i class="stride-dot" style="background:${
						STRIDE_MAP_COLORS.alarm
					}"></i>${__("Alarm")}</span>
				</div>
				<div class="stride-map-summary">
					<span class="vehicle-count-text">${__("Loading...")}</span>
				</div>
			</div>
		`).appendTo(this.page.main);
	}

	setup_map() {
		this.map = L.map("stride-vehicle-map").setView(STRIDE_DEFAULT_CENTER, 12);

		L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
			attribution:
				'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
			maxZoom: 19,
		}).addTo(this.map);

		this.marker_layer = L.layerGroup().addTo(this.map);
		this.route_layer = L.layerGroup().addTo(this.map);

		// The page can be built while hidden, leaving Leaflet with a zero-sized
		// container until it is told to measure again.
		setTimeout(() => this.map.invalidateSize(), 200);
	}

	// ----------------------------------------------------------------
	// Live positions
	// ----------------------------------------------------------------

	load_vehicles() {
		frappe
			.call({
				method:
					"stride.stride.page.vehicle_map.vehicle_map.get_vehicle_locations",
				freeze: false,
			})
			.then((r) => this.render_markers(r.message || []));
	}

	render_markers(locations) {
		const bounds = [];
		const seen = new Set();

		locations.forEach((loc) => {
			const latlng = [parseFloat(loc.latitude), parseFloat(loc.longitude)];
			if (isNaN(latlng[0]) || isNaN(latlng[1])) return;

			bounds.push(latlng);
			seen.add(loc.vehicle);
			this.upsert_marker(loc, latlng);
		});

		// Markers are moved rather than rebuilt, so a popup the user opened stays
		// open across the 30 second refresh.
		Object.keys(this.markers).forEach((vehicle) => {
			if (!seen.has(vehicle)) {
				this.marker_layer.removeLayer(this.markers[vehicle]);
				delete this.markers[vehicle];
			}
		});

		if (bounds.length && !this.route_layer.getLayers().length) {
			this.map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
		}

		this.update_summary(locations);
	}

	upsert_marker(loc, latlng) {
		let marker = this.markers[loc.vehicle];

		if (marker) {
			marker.stride_loc = loc;
			marker.setLatLng(latlng);
			marker.setStyle({ fillColor: stride_marker_color(loc) });
			return;
		}

		marker = stride_dot_marker(latlng, stride_marker_color(loc), 9);
		marker.stride_loc = loc;

		// Built on open, so a refresh does not render popups nobody is looking at.
		marker.bindPopup(() => stride_popup_html(marker.stride_loc));
		marker.bindTooltip(loc.license_plate || loc.vehicle, {
			direction: "top",
			offset: [0, -10],
		});
		marker.on("click", () => this.vehicle_field.set_value(loc.vehicle));
		marker.addTo(this.marker_layer);

		this.markers[loc.vehicle] = marker;
	}

	update_summary(locations) {
		if (!locations.length) {
			this.map_wrapper
				.find(".vehicle-count-text")
				.text(__("No vehicles tracked"));
			return;
		}

		const alarms = locations.filter((l) => l.alarm_code).length;
		const parts = [`${locations.length} ${__("tracked")}`];

		if (alarms) {
			parts.push(
				`<span style="color:${STRIDE_MAP_COLORS.alarm}">${alarms} ${__(
					"with alarms"
				)}</span>`
			);
		}

		this.map_wrapper.find(".vehicle-count-text").html(parts.join(" &middot; "));
	}

	// ----------------------------------------------------------------
	// Selection and route replay
	// ----------------------------------------------------------------

	on_vehicle_change() {
		const vehicle = this.vehicle_field.get_value();

		if (vehicle === this.selected_vehicle) {
			return;
		}

		this.selected_vehicle = vehicle;
		this.route_button.prop("disabled", !vehicle);
		this.clear_route();

		if (!vehicle) {
			this.load_vehicles();
			return;
		}

		const marker = this.markers[vehicle];

		if (!marker) {
			frappe.show_alert({
				message: __("No GPS data for {0}", [vehicle]),
				indicator: "orange",
			});
			return;
		}

		this.map.setView(marker.getLatLng(), 16);
		marker.openPopup();
	}

	prompt_route() {
		const vehicle = this.vehicle_field.get_value();
		if (!vehicle) return;

		frappe.prompt(
			[
				{
					fieldname: "from_date",
					fieldtype: "Datetime",
					label: __("From"),
					reqd: 1,
					default: stride_days_ago(1),
				},
				{
					fieldname: "to_date",
					fieldtype: "Datetime",
					label: __("To"),
					reqd: 1,
					default: frappe.datetime.now_datetime(),
				},
			],
			(values) => this.load_route(vehicle, values.from_date, values.to_date),
			__("Show Route"),
			__("Draw")
		);
	}

	load_route(vehicle, from_date, to_date) {
		frappe
			.call({
				method: "stride.stride.page.vehicle_map.vehicle_map.get_vehicle_route",
				args: { vehicle, from_date, to_date },
				freeze: true,
				freeze_message: __("Loading route..."),
			})
			.then((r) =>
				this.draw_route(r.message || [], vehicle, from_date, to_date)
			);
	}

	draw_route(points, vehicle, from_date, to_date) {
		this.clear_route();

		const path = points
			.map((p) => [parseFloat(p.latitude), parseFloat(p.longitude)])
			.filter(([lat, lng]) => !isNaN(lat) && !isNaN(lng));

		if (path.length < 2) {
			frappe.show_alert({
				message: __("Not enough points to draw a route."),
				indicator: "orange",
			});
			return;
		}

		L.polyline(path, {
			color: STRIDE_MAP_COLORS.route,
			weight: 4,
			opacity: 0.8,
		}).addTo(this.route_layer);

		stride_endpoint_marker(path[0], __("Start")).addTo(this.route_layer);
		stride_endpoint_marker(path[path.length - 1], __("End")).addTo(
			this.route_layer
		);

		this.map.fitBounds(path, { padding: [50, 50] });
		this.load_route_alarms(vehicle, from_date, to_date);
	}

	load_route_alarms(vehicle, from_date, to_date) {
		frappe
			.call({
				method: "stride.stride.page.vehicle_map.vehicle_map.get_vehicle_alarms",
				args: { vehicle, from_date, to_date },
			})
			.then((r) => {
				(r.message || []).forEach((alarm) => {
					if (!alarm.latitude || !alarm.longitude) return;

					stride_dot_marker(
						[alarm.latitude, alarm.longitude],
						STRIDE_MAP_COLORS.alarm,
						7
					)
						.bindPopup(stride_alarm_popup_html(alarm))
						.addTo(this.route_layer);
				});
			});
	}

	clear_route() {
		this.route_layer.clearLayers();
	}

	// ----------------------------------------------------------------
	// Auto refresh
	// ----------------------------------------------------------------

	resume() {
		if (this.map && this.auto_refresh_field?.get_value()) {
			this.map.invalidateSize();
			this.load_vehicles();
			this.start_auto_refresh();
		}
	}

	start_auto_refresh() {
		this.stop_auto_refresh();
		this.refresh_interval = setInterval(
			() => this.load_vehicles(),
			STRIDE_REFRESH_MS
		);
	}

	stop_auto_refresh() {
		if (this.refresh_interval) {
			clearInterval(this.refresh_interval);
			this.refresh_interval = null;
		}
	}
}

// frappe.datetime.add_days returns ISO-8601 with an offset, which a Datetime
// control cannot parse. Build the value in the format now_datetime() returns.
function stride_days_ago(days) {
	return moment().subtract(days, "days").format(frappe.defaultDatetimeFormat);
}

function stride_marker_color(loc) {
	if (loc.alarm_code) return STRIDE_MAP_COLORS.alarm;
	if (parseFloat(loc.speed || 0) > STRIDE_MOVING_SPEED_KMH)
		return STRIDE_MAP_COLORS.moving;
	return STRIDE_MAP_COLORS.idle;
}

function stride_dot_marker(latlng, color, radius) {
	return L.circleMarker(latlng, {
		radius,
		fillColor: color,
		color: "#fff",
		weight: 2,
		opacity: 1,
		fillOpacity: 0.9,
	});
}

function stride_endpoint_marker(latlng, label) {
	return stride_dot_marker(latlng, STRIDE_MAP_COLORS.route, 6).bindTooltip(
		label,
		{
			permanent: true,
			direction: "top",
			offset: [0, -8],
		}
	);
}

function stride_popup_html(loc) {
	const escape = frappe.utils.escape_html;
	const speed = loc.speed ? `${flt(loc.speed, 1)} km/h` : __("Stationary");
	const position =
		loc.address || `${flt(loc.latitude, 5)}, ${flt(loc.longitude, 5)}`;

	const alarm = loc.alarm_code
		? `<div class="stride-popup-alarm">
				${escape(loc.alarm_code)}${
				loc.alarm_description ? ` &mdash; ${escape(loc.alarm_description)}` : ""
		  }
		   </div>`
		: "";

	return `
		<div class="stride-popup">
			<div class="stride-popup-title">${escape(
				loc.license_plate || loc.vehicle
			)}</div>
			<div class="stride-popup-subtitle">${escape(
				`${loc.make || ""} ${loc.model || ""}`.trim()
			)}</div>
			<dl class="stride-popup-facts">
				<dt>${__("Position")}</dt><dd>${escape(position)}</dd>
				<dt>${__("Speed")}</dt><dd>${speed}</dd>
				<dt>${__("Ignition")}</dt><dd>${loc.acc_status ? __("On") : __("Off")}</dd>
				<dt>${__("Last seen")}</dt><dd>${frappe.datetime.str_to_user(
		loc.timestamp
	)}</dd>
			</dl>
			${alarm}
			<a href="/desk/vehicle/${encodeURIComponent(loc.vehicle)}">${__(
		"Open Vehicle"
	)} &rarr;</a>
		</div>
	`;
}

function stride_alarm_popup_html(alarm) {
	const escape = frappe.utils.escape_html;

	return `
		<div class="stride-popup">
			<div class="stride-popup-title">${escape(alarm.alarm_code)}</div>
			<div class="stride-popup-subtitle">${frappe.datetime.str_to_user(
				alarm.alarm_time
			)}</div>
			<dl class="stride-popup-facts">
				<dt>${__("Speed")}</dt><dd>${flt(alarm.speed, 1)} km/h</dd>
				${
					alarm.address
						? `<dt>${__("Address")}</dt><dd>${escape(alarm.address)}</dd>`
						: ""
				}
			</dl>
		</div>
	`;
}
