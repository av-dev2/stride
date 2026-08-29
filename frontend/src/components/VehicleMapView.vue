<template>
	<div ref="mapContainer" class="w-full h-full"></div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount, nextTick } from "vue";
import L from "leaflet";

const props = defineProps({
	locations: {
		type: Array,
		default: () => [],
	},
	selectedVehicle: {
		type: String,
		default: null,
	},
});

const emit = defineEmits(["vehicle-selected"]);

const mapContainer = ref(null);
let map = null;
let markers = {};
let markerGroup = null;

// Fix Leaflet default icon path issues in bundled apps
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
	iconRetinaUrl: new URL(
		"leaflet/dist/images/marker-icon-2x.png",
		import.meta.url
	).href,
	iconUrl: new URL("leaflet/dist/images/marker-icon.png", import.meta.url).href,
	shadowUrl: new URL("leaflet/dist/images/marker-shadow.png", import.meta.url)
		.href,
});

// Marker colors
function getMarkerColor(loc) {
	if (loc.alert_type) return "#e74c3c";
	if (parseFloat(loc.speed || 0) > 2) return "#2ecc71";
	return "#3498db";
}

function getStatusLabel(loc) {
	if (loc.alert_type) return "Alert";
	if (parseFloat(loc.speed || 0) > 2) return "Moving";
	return "Idle";
}

function initMap() {
	if (!mapContainer.value) return;

	map = L.map(mapContainer.value, {
		zoomControl: true,
		attributionControl: true,
	}).setView([-6.7924, 39.2083], 12);

	L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
		attribution:
			'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
		maxZoom: 19,
	}).addTo(map);

	markerGroup = L.layerGroup().addTo(map);
}

function renderMarkers(locs) {
	if (!map || !markerGroup) return;

	markerGroup.clearLayers();
	markers = {};

	const bounds = [];

	locs.forEach((loc) => {
		const lat = parseFloat(loc.latitude);
		const lng = parseFloat(loc.longitude);
		if (isNaN(lat) || isNaN(lng)) return;

		const latlng = [lat, lng];
		bounds.push(latlng);

		const color = getMarkerColor(loc);
		const statusLabel = getStatusLabel(loc);

		const marker = L.circleMarker(latlng, {
			radius: 10,
			fillColor: color,
			color: "#fff",
			weight: 2,
			opacity: 1,
			fillOpacity: 0.85,
		});

		// Build popup
		const speedDisplay = loc.speed
			? `${parseFloat(loc.speed).toFixed(1)} km/h`
			: "Stationary";
		const alertHtml = loc.alert_type
			? `<div style="color:#e74c3c;font-weight:600;margin-top:6px;">
           ⚠️ ${loc.alert_type}: ${loc.alert_message || ""}
         </div>`
			: "";

		marker.bindPopup(`
      <div style="min-width:200px;font-size:13px;line-height:1.6;">
        <div style="font-weight:700;font-size:15px;margin-bottom:4px;">
          ${loc.license_plate || loc.vehicle}
        </div>
        <div style="color:#888;margin-bottom:6px;">
          ${loc.make || ""} ${loc.model || ""}
        </div>
        <div>📍 ${loc.address || `${lat.toFixed(5)}, ${lng.toFixed(5)}`}</div>
        <div>🏎️ ${speedDisplay}</div>
        <div>📡 Status: <strong style="color:${color};">${statusLabel}</strong></div>
        ${alertHtml}
        <div style="margin-top:8px;">
          <a href="/desk/vehicle/${loc.vehicle}"
             style="color:#2490ef;text-decoration:none;">
            Open Vehicle →
          </a>
        </div>
      </div>
    `);

		marker.bindTooltip(loc.license_plate || loc.vehicle, {
			permanent: false,
			direction: "top",
			offset: [0, -12],
		});

		marker.on("click", () => {
			emit("vehicle-selected", loc.vehicle);
		});

		marker.addTo(markerGroup);
		markers[loc.vehicle] = marker;
	});

	// Fit bounds
	if (bounds.length > 0) {
		map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
	}
}

function focusOnVehicle(loc) {
	if (!map) return;
	const marker = markers[loc.vehicle];
	if (marker) {
		map.setView(marker.getLatLng(), 16, { animate: true });
		marker.openPopup();
	}
}

// Expose to parent
defineExpose({ focusOnVehicle });

// Watch for location changes
watch(
	() => props.locations,
	(newLocs) => {
		nextTick(() => renderMarkers(newLocs));
	},
	{ deep: true }
);

// Watch for selected vehicle highlight
watch(
	() => props.selectedVehicle,
	(vehicleName) => {
		if (vehicleName && markers[vehicleName]) {
			const marker = markers[vehicleName];
			map.setView(marker.getLatLng(), 16, { animate: true });
			marker.openPopup();
		}
	}
);

onMounted(() => {
	nextTick(() => {
		initMap();
		if (props.locations.length) {
			renderMarkers(props.locations);
		}
	});
});

onBeforeUnmount(() => {
	if (map) {
		map.remove();
		map = null;
	}
});
</script>

<style scoped>
/* Ensure Leaflet controls are visible above other elements */
:deep(.leaflet-control-zoom a) {
	color: #333 !important;
	background: #fff !important;
}

:deep(.leaflet-popup-content-wrapper) {
	border-radius: 8px !important;
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}
</style>
