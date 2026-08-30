<template>
	<div
		class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/40"
	>
		<!-- ── Top Navigation Bar ────────────────────────────────────── -->
		<header
			class="bg-white/80 backdrop-blur border-b border-gray-100 sticky top-0 z-30"
		>
			<div
				class="max-w-3xl mx-auto px-4 h-14 flex items-center justify-between"
			>
				<div class="flex items-center gap-2.5">
					<div
						class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shadow-sm"
					>
						<FeatherIcon name="truck" class="w-5 h-5 text-white" />
					</div>
					<span class="font-bold text-gray-900 text-base tracking-tight"
						>Stride</span
					>
				</div>

				<div class="flex items-center gap-3">
					<span
						v-if="loggedInUserName"
						class="text-sm text-gray-600 font-medium hidden sm:inline"
					>
						{{ loggedInUserName }}
					</span>
					<button
						id="stride-logout-btn"
						@click="logout"
						class="flex items-center gap-1.5 text-sm text-gray-500 hover:text-red-600 transition-colors px-2 py-1 rounded-lg hover:bg-red-50"
					>
						<FeatherIcon name="log-out" class="w-4 h-4" />
						<span class="hidden sm:inline">Logout</span>
					</button>
				</div>
			</div>
		</header>

		<main class="max-w-3xl mx-auto px-4 py-6 space-y-4">
			<div class="flex items-center justify-between">
				<div>
					<h1 class="text-lg font-bold text-gray-900 tracking-tight">
						Vehicles
					</h1>
					<p class="text-xs text-gray-400 mt-0.5">
						{{ vehicles.length }} vehicle{{ vehicles.length !== 1 ? "s" : "" }}
					</p>
				</div>

				<!-- List / Card toggle -->
				<div
					class="flex items-center gap-1 bg-white border border-gray-200 rounded-lg p-1"
				>
					<button
						id="stride-view-list"
						@click="viewMode = 'list'"
						class="p-1.5 rounded-md transition-colors"
						:class="
							viewMode === 'list'
								? 'bg-blue-600 text-white'
								: 'text-gray-400 hover:text-gray-600'
						"
					>
						<FeatherIcon name="list" class="w-4 h-4" />
					</button>
					<button
						id="stride-view-card"
						@click="viewMode = 'card'"
						class="p-1.5 rounded-md transition-colors"
						:class="
							viewMode === 'card'
								? 'bg-blue-600 text-white'
								: 'text-gray-400 hover:text-gray-600'
						"
					>
						<FeatherIcon name="grid" class="w-4 h-4" />
					</button>
				</div>
			</div>

			<!-- Loading -->
			<div v-if="loading" class="space-y-3">
				<div
					v-for="i in 4"
					:key="i"
					class="bg-white rounded-2xl h-20 animate-pulse border border-gray-100"
				/>
			</div>

			<!-- Empty -->
			<div
				v-else-if="vehicles.length === 0"
				class="bg-white border border-gray-100 rounded-2xl p-10 text-center text-gray-400"
			>
				<FeatherIcon name="truck" class="w-8 h-8 mx-auto mb-2 opacity-50" />
				<p class="text-sm">No vehicles found.</p>
			</div>

			<!-- List view -->
			<div v-else-if="viewMode === 'list'" class="space-y-2">
				<button
					v-for="vehicle in vehicles"
					:key="vehicle.name"
					@click="openVehicle(vehicle)"
					class="w-full flex items-center gap-3 bg-white rounded-xl border border-gray-100 p-3 shadow-sm hover:shadow-md hover:border-blue-200 transition-all text-left"
				>
					<div
						class="w-11 h-11 rounded-lg bg-blue-50 flex items-center justify-center flex-shrink-0 overflow-hidden"
					>
						<img
							v-if="vehicle.vehicle_image"
							:src="vehicle.vehicle_image"
							class="w-full h-full object-cover"
						/>
						<FeatherIcon v-else name="truck" class="w-5 h-5 text-blue-400" />
					</div>

					<div class="min-w-0 flex-1">
						<div class="flex items-center gap-2">
							<p class="font-semibold text-gray-900 text-sm truncate">
								{{ vehicleLabel(vehicle) }}
							</p>
							<span
								class="text-[10px] font-semibold px-1.5 py-0.5 rounded-full flex-shrink-0"
								:class="statusClass(vehicle.vehicle_status)"
							>
								{{ vehicle.vehicle_status || "—" }}
							</span>
						</div>
						<p class="text-xs text-gray-400 truncate">
							{{ vehicle.customer_name || "No active customer" }}
						</p>
					</div>

					<div
						v-if="vehicle.contract_start || vehicle.contract_end"
						class="text-right text-xs text-gray-400 flex-shrink-0 hidden sm:block"
					>
						<p>{{ vehicle.contract_start || "—" }}</p>
						<p>{{ vehicle.contract_end || "—" }}</p>
					</div>

					<FeatherIcon
						name="chevron-right"
						class="w-4 h-4 text-gray-300 flex-shrink-0"
					/>
				</button>
			</div>

			<!-- Card view -->
			<div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-3">
				<button
					v-for="vehicle in vehicles"
					:key="vehicle.name"
					@click="openVehicle(vehicle)"
					class="bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md hover:border-blue-200 transition-all text-left overflow-hidden"
				>
					<div
						class="h-24 bg-gradient-to-br from-blue-50/40 to-indigo-50/30 flex items-center justify-center border-b border-gray-100 relative"
					>
						<img
							v-if="vehicle.vehicle_image"
							:src="vehicle.vehicle_image"
							class="object-cover w-full h-full opacity-80"
						/>
						<FeatherIcon v-else name="truck" class="w-8 h-8 text-blue-300" />
						<span
							class="absolute top-2 right-2 text-[10px] font-semibold px-1.5 py-0.5 rounded-full"
							:class="statusClass(vehicle.vehicle_status)"
						>
							{{ vehicle.vehicle_status || "—" }}
						</span>
					</div>
					<div class="p-3">
						<p class="font-semibold text-gray-900 text-sm truncate">
							{{ vehicleLabel(vehicle) }}
						</p>
						<p class="text-xs text-gray-400 truncate mt-0.5">
							{{ vehicle.customer_name || "No active customer" }}
						</p>
						<div
							v-if="vehicle.contract_start || vehicle.contract_end"
							class="flex items-center justify-between text-[11px] text-gray-400 mt-2"
						>
							<span>{{ vehicle.contract_start || "—" }}</span>
							<FeatherIcon name="arrow-right" class="w-3 h-3" />
							<span>{{ vehicle.contract_end || "—" }}</span>
						</div>
					</div>
				</button>
			</div>
		</main>
	</div>
</template>

<script setup>
import { ref, computed, inject, onMounted } from "vue";
import { useRouter } from "vue-router";
import { createResource } from "frappe-ui";

const session = inject("$session");
const router = useRouter();

const loading = ref(true);
const viewMode = ref("list");
const vehicles = computed(() => vehiclesResource.data?.vehicles ?? []);
const loggedInUserName = computed(
	() => vehiclesResource.data?.logged_in_user_name
);

const vehiclesResource = createResource({
	url: "stride.api.pwa.get_manager_vehicles",
	method: "GET",
	auto: false,
	onSuccess() {
		loading.value = false;
	},
	onError() {
		loading.value = false;
	},
});

onMounted(() => vehiclesResource.fetch());

function vehicleLabel(vehicle) {
	return (
		[vehicle.make, vehicle.model].filter(Boolean).join(" ") ||
		vehicle.license_plate ||
		vehicle.name
	);
}

function statusClass(status) {
	const map = {
		Available: "bg-emerald-100 text-emerald-700",
		Rented: "bg-blue-100 text-blue-700",
		"Owned by Client": "bg-gray-200 text-gray-600",
		Maintenance: "bg-amber-100 text-amber-700",
	};
	return map[status] ?? "bg-gray-100 text-gray-600";
}

function openVehicle(vehicle) {
	router.push({ name: "VehicleDetail", params: { vehicle: vehicle.name } });
}

async function logout() {
	await session.logout();
}
</script>
