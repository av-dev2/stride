// Copyright (c) 2024, elius-dev and contributors
// For license information, please see license.txt

frappe.pages["vehicle-map"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Vehicle Map"),
		single_column: true,
	});

	frappe.breadcrumbs.add("Stride");

	// Load Leaflet CSS + JS from CDN, then initialize
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

class StrideVehicleMap {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.page = wrapper.page;
		this.markers = {};
		this.route_layer = null;
		this.refresh_interval = null;

		setTimeout(() => {
			this.setup_page();
			this.setup_map();
			this.load_vehicles();
			this.start_auto_refresh();
		}, 100);
	}

	setup_page() {
		// Refresh button
		this.page.set_primary_action(
			__("Refresh"),
			() => this.load_vehicles(),
			"refresh"
		);

		// Vehicle filter
		this.vehicle_field = this.page.add_field({
			fieldtype: "Link",
			fieldname: "vehicle",
			options: "Vehicle",
			label: __("Vehicle"),
			change: () => {
				const v = this.vehicle_field.get_value();
				if (v) {
					this.focus_vehicle(v);
				} else {
					this.load_vehicles();
				}
			},
		});

		// Auto-refresh toggle
		this.auto_refresh_field = this.page.add_field({
			fieldtype: "Check",
			fieldname: "auto_refresh",
			label: __("Auto Refresh (30s)"),
			default: 1,
			change: () => {
				if (this.auto_refresh_field.get_value()) {
					this.start_auto_refresh();
				} else {
					this.stop_auto_refresh();
				}
			},
		});

		// Map container
		this.map_wrapper = $(`
			<div class="stride-map-container" style="position: relative;">
				<div id="stride-vehicle-map" style="
					height: calc(100vh - 200px);
					min-height: 500px;
					width: 100%;
					border-radius: 8px;
					border: 1px solid var(--border-color);
				"></div>
				<div class="stride-map-legend" style="
					position: absolute;
					bottom: 16px;
					left: 16px;
					background: var(--card-bg);
					border-radius: 8px;
					padding: 12px 16px;
					box-shadow: 0 2px 8px rgba(0,0,0,0.15);
					z-index: 1000;
					font-size: 12px;
				">
					<div style="font-weight: 600; margin-bottom: 6px;">Legend</div>
					<div style="display: flex; gap: 12px; flex-wrap: wrap;">
						<span>🟢 Moving</span>
						<span>🔵 Idle</span>
						<span>🔴 Alert</span>
					</div>
				</div>
				<div class="stride-vehicle-count" style="
					position: absolute;
					top: 16px;
					right: 16px;
					background: var(--card-bg);
					border-radius: 8px;
					padding: 8px 14px;
					box-shadow: 0 2px 8px rgba(0,0,0,0.15);
					z-index: 1000;
					font-size: 13px;
					font-weight: 600;
				">
					<span class="vehicle-count-text">Loading...</span>
				</div>
			</div>
		`).appendTo(this.page.main);
	}

	setup_map() {
		// Default center: Dar es Salaam, Tanzania
		this.map = L.map("stride-vehicle-map").setView([-6.7924, 39.2083], 12);

		// OpenStreetMap tiles
		L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
			attribution:
				'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
			maxZoom: 19,
		}).addTo(this.map);
	}

	load_vehicles() {
		frappe.call({
			method:
				"stride.stride.page.vehicle_map.vehicle_map.get_vehicle_locations",
			freeze: false,
			callback: (r) => {
				if (r.message) {
					this.render_markers(r.message);
				}
			},
		});
	}

	render_markers(locations) {
		// Clear existing markers
		Object.values(this.markers).forEach((m) => this.map.removeLayer(m));
		this.markers = {};

		if (!locations.length) {
			this.map_wrapper.find(".vehicle-count-text").text("No vehicles tracked");
			return;
		}

		const bounds = [];

		locations.forEach((loc) => {
			const lat = parseFloat(loc.latitude);
			const lng = parseFloat(loc.longitude);

			if (isNaN(lat) || isNaN(lng)) return;

			const latlng = [lat, lng];
			bounds.push(latlng);

			// Determine marker color
			let color = "#3498db"; // idle (blue)
			let emoji = "🔵";

			if (loc.alert_type) {
				color = "#e74c3c"; // alert (red)
				emoji = "🔴";
			} else if (parseFloat(loc.speed || 0) > 2) {
				color = "#2ecc71"; // moving (green)
				emoji = "🟢";
			}

			// Custom circle marker
			const marker = L.circleMarker(latlng, {
				radius: 10,
				fillColor: color,
				color: "#fff",
				weight: 2,
				opacity: 1,
				fillOpacity: 0.85,
			}).addTo(this.map);

			// Popup content
			const speed_display = loc.speed
				? `${parseFloat(loc.speed).toFixed(1)} km/h`
				: "N/A";
			const time_display = loc.timestamp
				? frappe.datetime.str_to_user(loc.timestamp)
				: "Unknown";
			const alert_html = loc.alert_type
				? `<div style="color: #e74c3c; font-weight: 600; margin-top: 4px;">
					⚠️ ${loc.alert_type}: ${loc.alert_message || ""}
				   </div>`
				: "";

			marker.bindPopup(`
				<div style="min-width: 200px; font-size: 13px;">
					<div style="font-weight: 700; font-size: 15px; margin-bottom: 6px;">
						${emoji} ${loc.license_plate || loc.vehicle}
					</div>
					<div style="color: #666; margin-bottom: 2px;">
						${loc.make || ""} ${loc.model || ""}
					</div>
					<hr style="margin: 6px 0; border-color: #eee;">
					<div>📍 ${loc.address || `${lat.toFixed(5)}, ${lng.toFixed(5)}`}</div>
					<div>🏎️ Speed: ${speed_display}</div>
					<div>🕐 Last update: ${time_display}</div>
					${alert_html}
					<div style="margin-top: 8px;">
						<a href="/desk/vehicle/${loc.vehicle}" style="color: #2490ef;">
							Open Vehicle →
						</a>
					</div>
				</div>
			`);

			// Label
			marker.bindTooltip(loc.license_plate || loc.vehicle, {
				permanent: false,
				direction: "top",
				offset: [0, -10],
			});

			this.markers[loc.vehicle] = marker;
		});

		// Fit map to bounds
		if (bounds.length > 0) {
			this.map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
		}

		// Update counter
		const alert_count = locations.filter((l) => l.alert_type).length;
		let count_text = `${locations.length} vehicle${
			locations.length !== 1 ? "s" : ""
		} tracked`;
		if (alert_count > 0) {
			count_text += ` • <span style="color: #e74c3c;">${alert_count} alert${
				alert_count !== 1 ? "s" : ""
			}</span>`;
		}
		this.map_wrapper.find(".vehicle-count-text").html(count_text);
	}

	focus_vehicle(vehicle) {
		const marker = this.markers[vehicle];
		if (marker) {
			this.map.setView(marker.getLatLng(), 16);
			marker.openPopup();
		} else {
			frappe.show_alert({
				message: __("No GPS data for {0}", [vehicle]),
				indicator: "orange",
			});
		}
	}

	start_auto_refresh() {
		this.stop_auto_refresh();
		this.refresh_interval = setInterval(() => {
			this.load_vehicles();
		}, 30000);
	}

	stop_auto_refresh() {
		if (this.refresh_interval) {
			clearInterval(this.refresh_interval);
			this.refresh_interval = null;
		}
	}
}
