<template>
	<div class="flex flex-col h-screen">
		<!-- Header -->
		<div
			class="flex items-center justify-between px-5 py-3 bg-white border-b border-gray-200"
		>
			<div class="flex items-center gap-3">
				<router-link
					to="/"
					class="text-gray-400 hover:text-gray-600 transition-colors"
				>
					<FeatherIcon name="arrow-left" class="w-5 h-5" />
				</router-link>
				<h1 class="text-lg font-semibold text-gray-900">Vehicle Map</h1>
				<Badge v-if="vehicleCount > 0" variant="subtle" theme="blue">
					{{ vehicleCount }} vehicle{{ vehicleCount !== 1 ? "s" : "" }}
				</Badge>
				<Badge v-if="alertCount > 0" variant="subtle" theme="red">
					{{ alertCount }} alert{{ alertCount !== 1 ? "s" : "" }}
				</Badge>
			</div>

			<div class="flex items-center gap-3">
				<label class="flex items-center gap-2 text-sm text-gray-600">
					<input
						type="checkbox"
						v-model="autoRefresh"
						class="rounded border-gray-300"
					/>
					Auto-refresh (30s)
				</label>
				<Button
					variant="solid"
					@click="fetchLocations"
					:loading="loading"
					icon-left="refresh-cw"
				>
					Refresh
				</Button>
			</div>
		</div>

		<!-- Map + Sidebar -->
		<div class="flex flex-1 overflow-hidden">
			<!-- Sidebar: Vehicle List -->
			<div
				class="w-72 bg-white border-r border-gray-200 overflow-y-auto flex-shrink-0"
			>
				<div class="p-3 border-b border-gray-100">
					<input
						v-model="searchQuery"
						type="text"
						placeholder="Search vehicles..."
						class="w-full px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
					/>
				</div>

				<div v-if="filteredLocations.length === 0" class="p-4 text-center">
					<FeatherIcon
						name="map-pin"
						class="w-8 h-8 text-gray-300 mx-auto mb-2"
					/>
					<p class="text-sm text-gray-400">No vehicles tracked</p>
				</div>

				<div
					v-for="loc in filteredLocations"
					:key="loc.vehicle"
					@click="focusVehicle(loc)"
					class="px-4 py-3 border-b border-gray-50 cursor-pointer hover:bg-blue-50 transition-colors"
					:class="{
						'bg-blue-50 border-l-2 border-l-blue-500':
							selectedVehicle === loc.vehicle,
					}"
				>
					<div class="flex items-center justify-between mb-1">
						<span class="font-medium text-sm text-gray-900">
							{{ statusEmoji(loc) }}
							{{ loc.license_plate || loc.vehicle }}
						</span>
						<Badge v-if="loc.alert_type" variant="subtle" theme="red" size="sm">
							Alert
						</Badge>
					</div>
					<div class="text-xs text-gray-500">
						{{ loc.make }} {{ loc.model }}
					</div>
					<div class="text-xs text-gray-400 mt-1">
						{{
							loc.speed ? parseFloat(loc.speed).toFixed(1) + " km/h" : "Idle"
						}}
						· {{ formatTimestamp(loc.timestamp) }}
					</div>
				</div>
			</div>

			<!-- Map Container -->
			<div class="flex-1 relative">
				<VehicleMapView
					ref="mapRef"
					:locations="locations"
					:selected-vehicle="selectedVehicle"
					@vehicle-selected="onVehicleSelected"
				/>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from "vue";
import { createResource } from "frappe-ui";
import VehicleMapView from "../components/VehicleMapView.vue";

const locations = ref([]);
const loading = ref(false);
const searchQuery = ref("");
const selectedVehicle = ref(null);
const autoRefresh = ref(true);
const mapRef = ref(null);

let refreshTimer = null;

// Resource for fetching vehicle locations
const vehicleLocations = createResource({
	url: "stride.stride.page.vehicle_map.vehicle_map.get_vehicle_locations",
	auto: false,
	onSuccess(data) {
		locations.value = data || [];
		loading.value = false;
	},
	onError() {
		loading.value = false;
	},
});

// Computed
const vehicleCount = computed(() => locations.value.length);
const alertCount = computed(
	() => locations.value.filter((l) => l.alert_type).length
);

const filteredLocations = computed(() => {
	if (!searchQuery.value) return locations.value;
	const q = searchQuery.value.toLowerCase();
	return locations.value.filter(
		(l) =>
			(l.license_plate || "").toLowerCase().includes(q) ||
			(l.vehicle || "").toLowerCase().includes(q) ||
			(l.make || "").toLowerCase().includes(q) ||
			(l.model || "").toLowerCase().includes(q)
	);
});

// Methods
function fetchLocations() {
	loading.value = true;
	vehicleLocations.fetch();
}

function focusVehicle(loc) {
	selectedVehicle.value = loc.vehicle;
	if (mapRef.value) {
		mapRef.value.focusOnVehicle(loc);
	}
}

function onVehicleSelected(vehicleName) {
	selectedVehicle.value = vehicleName;
}

function statusEmoji(loc) {
	if (loc.alert_type) return "🔴";
	if (parseFloat(loc.speed || 0) > 2) return "🟢";
	return "🔵";
}

function formatTimestamp(ts) {
	if (!ts) return "—";
	const d = new Date(ts);
	return d.toLocaleString("en-GB", {
		day: "2-digit",
		month: "short",
		hour: "2-digit",
		minute: "2-digit",
	});
}

function startAutoRefresh() {
	stopAutoRefresh();
	refreshTimer = setInterval(fetchLocations, 30000);
}

function stopAutoRefresh() {
	if (refreshTimer) {
		clearInterval(refreshTimer);
		refreshTimer = null;
	}
}

// Watch auto-refresh toggle
watch(autoRefresh, (val) => {
	if (val) startAutoRefresh();
	else stopAutoRefresh();
});

// Lifecycle
onMounted(() => {
	fetchLocations();
	if (autoRefresh.value) startAutoRefresh();
});

onBeforeUnmount(() => {
	stopAutoRefresh();
});
</script>
