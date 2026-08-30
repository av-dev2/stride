<template>
	<div
		class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/40"
	>
		<!-- ── Top Navigation Bar ────────────────────────────────────── -->
		<header
			class="bg-white/80 backdrop-blur border-b border-gray-100 sticky top-0 z-30"
		>
			<div
				class="max-w-2xl mx-auto px-4 h-14 flex items-center justify-between"
			>
				<div class="flex items-center gap-2.5">
					<router-link
						:to="{ name: 'VehicleList' }"
						class="text-gray-400 hover:text-gray-600 transition-colors p-1 -ml-1"
					>
						<FeatherIcon name="arrow-left" class="w-5 h-5" />
					</router-link>
					<span class="font-bold text-gray-900 text-base tracking-tight"
						>Stride</span
					>
				</div>

				<div class="flex items-center gap-3">
					<span
						v-if="ctx?.customer_name"
						class="text-sm text-gray-600 font-medium hidden sm:inline"
					>
						{{ ctx.customer_name }}
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

		<!-- ── Main Content ──────────────────────────────────────────── -->
		<main class="max-w-2xl mx-auto px-4 py-6 space-y-6">
			<!-- Loading state -->
			<div v-if="loading" class="space-y-4">
				<div
					v-for="i in 4"
					:key="i"
					class="bg-white rounded-2xl h-28 animate-pulse border border-gray-100"
				/>
			</div>

			<!-- Error / no lease -->
			<div
				v-else-if="ctx?.error"
				class="bg-amber-50 border border-amber-200 rounded-2xl p-6 text-center"
			>
				<FeatherIcon
					name="alert-circle"
					class="w-10 h-10 text-amber-400 mx-auto mb-3"
				/>
				<p class="text-amber-800 font-medium">{{ ctx.message }}</p>
			</div>

			<template v-else-if="ctx">
				<!-- Welcome -->
				<div
					class="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-5 text-white shadow-lg shadow-blue-200/50"
				>
					<p class="text-blue-100 text-sm font-medium mb-0.5">Welcome back,</p>
					<h1 class="text-xl font-bold tracking-tight">
						{{ ctx.customer_name }}
					</h1>
					<div class="mt-3 flex items-center gap-2 text-blue-100 text-xs">
						<FeatherIcon name="check-circle" class="w-3.5 h-3.5" />
						<span>Lease {{ ctx.lease?.name }} · {{ ctx.lease?.status }}</span>
					</div>
				</div>

				<!-- ── Payment Summary Cards ───────────────────────── -->
				<section>
					<h2
						class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3 px-1"
					>
						Payment Summary
					</h2>
					<div
						v-if="totalPayments > 0"
						class="h-2 w-full bg-gray-100 rounded-full overflow-hidden flex gap-[2px] mb-4"
					>
						<div
							:style="{
								width: (ctx.payments.paid.count / totalPayments) * 100 + '%',
							}"
							class="h-full bg-green-500"
							title="Paid"
						/>
						<div
							:style="{
								width:
									(ctx.payments.invoiced.count / totalPayments) * 100 + '%',
							}"
							class="h-full bg-red-500"
							title="Pending"
						/>
						<div
							:style="{
								width:
									(ctx.payments.postponed.count / totalPayments) * 100 + '%',
							}"
							class="h-full bg-blue-900"
							title="Postponed"
						/>
					</div>
					<div class="grid grid-cols-3 gap-3">
						<button
							id="stride-card-paid"
							@click="openDetail('paid')"
							class="group bg-white rounded-2xl p-4 border border-gray-100 border-l-4 border-l-green-600 shadow-sm hover:shadow-md hover:border-green-300 transition-all duration-200 text-left"
						>
							<div
								class="w-9 h-9 rounded-xl bg-green-100 group-hover:bg-green-200 flex items-center justify-center mb-3 transition-colors"
							>
								<FeatherIcon
									name="check-circle"
									class="w-5 h-5 text-green-600"
								/>
							</div>
							<p class="text-2xl font-bold text-gray-900 leading-none">
								{{ ctx.payments.paid.count }}
							</p>
							<p class="text-xs text-green-600 mt-1 font-semibold">Paid</p>
						</button>

						<button
							id="stride-card-pending"
							@click="openDetail('invoiced')"
							class="group bg-white rounded-2xl p-4 border border-gray-100 border-l-4 border-l-red-500 shadow-sm hover:shadow-md hover:border-red-300 transition-all duration-200 text-left"
						>
							<div
								class="w-9 h-9 rounded-xl bg-red-100 group-hover:bg-red-200 flex items-center justify-center mb-3 transition-colors"
							>
								<FeatherIcon name="clock" class="w-5 h-5 text-red-600" />
							</div>
							<p class="text-2xl font-bold text-gray-900 leading-none">
								{{ ctx.payments.invoiced.count }}
							</p>
							<p class="text-xs text-red-600 mt-1 font-semibold">Pending</p>
						</button>

						<button
							id="stride-card-postponed"
							@click="openDetail('postponed')"
							class="group bg-white rounded-2xl p-4 border border-gray-100 border-l-4 border-l-blue-900 shadow-sm hover:shadow-md hover:border-blue-300 transition-all duration-200 text-left"
						>
							<div
								class="w-9 h-9 rounded-xl bg-blue-100 group-hover:bg-blue-200 flex items-center justify-center mb-3 transition-colors"
							>
								<FeatherIcon name="pause" class="w-5 h-5 text-blue-900" />
							</div>
							<p class="text-2xl font-bold text-gray-900 leading-none">
								{{ ctx.payments.postponed.count }}
							</p>
							<p class="text-xs text-blue-900 mt-1 font-semibold">Postponed</p>
						</button>
					</div>
				</section>

				<!-- ── Vehicle Detail Card ────────────────────────── -->
				<section v-if="ctx.vehicle">
					<h2
						class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3 px-1"
					>
						Vehicle
					</h2>
					<div
						class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden"
					>
						<div
							class="h-32 bg-gradient-to-br from-blue-50/40 to-indigo-50/30 flex items-center justify-center relative overflow-hidden border-b border-gray-100"
						>
							<img
								v-if="ctx.vehicle.vehicle_image"
								:src="ctx.vehicle.vehicle_image"
								:alt="vehicleLabel"
								class="object-cover w-full h-full opacity-80"
							/>
							<FeatherIcon
								v-else
								name="truck"
								class="w-14 h-14 mx-auto opacity-70 text-blue-400/80"
							/>
							<span
								class="absolute top-3 left-3 text-xs font-bold px-2.5 py-1 rounded-full bg-blue-600 text-white shadow-sm"
							>
								{{ vehicleLabel }}
							</span>
							<span
								class="absolute top-3 right-3 text-xs font-semibold px-2.5 py-1 rounded-full"
								:class="vehicleStatusClass"
							>
								{{ ctx.vehicle.vehicle_status || "—" }}
							</span>
						</div>

						<div class="p-4 space-y-3">
							<div class="grid grid-cols-4 gap-2 divide-x divide-gray-100">
								<div class="text-center">
									<p
										class="text-xs text-gray-400 uppercase tracking-wide font-medium"
									>
										Reg No
									</p>
									<p class="text-sm font-semibold text-blue-600 mt-0.5">
										{{ ctx.vehicle.license_plate }}
									</p>
								</div>
								<div class="text-center">
									<p
										class="text-xs text-gray-400 uppercase tracking-wide font-medium"
									>
										Year
									</p>
									<p class="text-sm font-semibold text-gray-800 mt-0.5">
										{{ ctx.vehicle.year_of_manufacture || "—" }}
									</p>
								</div>
								<div class="text-center">
									<p
										class="text-xs text-gray-400 uppercase tracking-wide font-medium"
									>
										Color
									</p>
									<p class="text-sm font-semibold text-gray-800 mt-0.5">
										{{ ctx.vehicle.color || "—" }}
									</p>
								</div>
								<div class="text-center">
									<p
										class="text-xs text-gray-400 uppercase tracking-wide font-medium"
									>
										Fuel
									</p>
									<p class="text-sm font-semibold text-gray-800 mt-0.5">
										{{ ctx.vehicle.fuel_type || "—" }}
									</p>
								</div>
							</div>

							<div
								class="bg-blue-50 border border-blue-100 rounded-xl p-3 grid grid-cols-3 gap-2 text-sm mt-1"
							>
								<div class="text-left">
									<p
										class="text-[10px] text-blue-600 uppercase tracking-wider font-semibold"
									>
										Rate
									</p>
									<p class="font-bold text-blue-950 mt-0.5">
										{{ formatCurrency(ctx.lease.rate) }} /
										{{ ctx.lease.period_type }}
									</p>
								</div>
								<div class="text-center">
									<p
										class="text-[10px] text-blue-600 uppercase tracking-wider font-semibold"
									>
										Contract Start
									</p>
									<p class="font-bold text-blue-950 mt-0.5">
										{{ ctx.lease.start_date }}
									</p>
								</div>
								<div class="text-right">
									<p
										class="text-[10px] text-blue-600 uppercase tracking-wider font-semibold"
									>
										Contract End
									</p>
									<p class="font-bold text-blue-950 mt-0.5">
										{{ ctx.lease.end_date }}
									</p>
								</div>
							</div>
						</div>
					</div>
				</section>
			</template>
		</main>

		<!-- ── Detail Drawer / Modal ─────────────────────────────────── -->
		<Transition name="drawer">
			<div
				v-if="detail.open"
				class="fixed inset-0 z-50 flex items-end sm:items-center justify-center"
			>
				<div
					class="absolute inset-0 bg-black/40 backdrop-blur-sm"
					@click="detail.open = false"
				/>

				<div
					class="relative w-full max-w-lg bg-white rounded-t-3xl sm:rounded-2xl shadow-2xl max-h-[85vh] flex flex-col"
				>
					<div
						class="flex items-center justify-between px-5 pt-5 pb-4 border-b border-gray-100 flex-shrink-0"
					>
						<div class="flex items-center gap-3">
							<div
								class="w-8 h-8 rounded-xl flex items-center justify-center"
								:class="detail.iconBg"
							>
								<span class="text-lg">{{ detail.icon }}</span>
							</div>
							<div>
								<h3 class="font-bold text-gray-900 text-base leading-tight">
									{{ detail.title }}
								</h3>
								<p class="text-xs text-gray-400">
									{{ detail.rows.length }} period{{
										detail.rows.length !== 1 ? "s" : ""
									}}
								</p>
							</div>
						</div>
						<button
							@click="detail.open = false"
							class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-400 hover:bg-gray-200 transition-colors"
						>
							<FeatherIcon name="x" class="w-4 h-4" />
						</button>
					</div>

					<div class="overflow-y-auto flex-1 px-4 py-3 space-y-2">
						<div
							v-for="row in detail.rows"
							:key="row.name"
							class="bg-gray-50 rounded-xl p-3.5 border border-gray-100"
						>
							<div class="flex items-start justify-between mb-2">
								<div>
									<span
										class="text-xs font-bold text-gray-400 uppercase tracking-wide"
										>Period {{ row.period }}</span
									>
									<p class="text-sm font-semibold text-gray-800 mt-0.5">
										{{ row.due_date }}
									</p>
								</div>
								<span class="text-sm font-bold text-gray-900">{{
									formatCurrency(row.amount)
								}}</span>
							</div>

							<div
								v-if="detail.type === 'paid' && row.payment_entry"
								class="flex items-center gap-1.5 mt-1"
							>
								<FeatherIcon
									name="check"
									class="w-3 h-3 text-emerald-500 flex-shrink-0"
								/>
								<span class="text-xs text-gray-500">{{
									row.payment_entry
								}}</span>
							</div>

							<div
								v-if="detail.type === 'invoiced' && row.sales_invoice"
								class="flex items-center gap-1.5 mt-1"
							>
								<FeatherIcon
									name="file-text"
									class="w-3 h-3 text-amber-500 flex-shrink-0"
								/>
								<span class="text-xs text-gray-500"
									>Invoice: {{ row.sales_invoice }}</span
								>
							</div>
						</div>

						<div
							v-if="detail.rows.length === 0"
							class="text-center py-10 text-gray-400"
						>
							<p class="text-sm">No records found.</p>
						</div>
					</div>
				</div>
			</div>
		</Transition>
	</div>
</template>

<script setup>
import { ref, reactive, computed, inject, onMounted } from "vue";
import { createResource } from "frappe-ui";

const props = defineProps({
	vehicle: { type: String, required: true },
});

const session = inject("$session");

const loading = ref(true);
const ctx = ref(null);

const pwaResource = createResource({
	url: "stride.api.pwa.get_vehicle_pwa_context",
	method: "GET",
	auto: false,
	onSuccess(data) {
		ctx.value = data;
		loading.value = false;
	},
	onError() {
		loading.value = false;
	},
});

onMounted(() => pwaResource.fetch({ vehicle: props.vehicle }));

const totalPayments = computed(() => {
	if (!ctx.value?.payments) return 0;
	return (
		(ctx.value.payments.paid?.count || 0) +
		(ctx.value.payments.invoiced?.count || 0) +
		(ctx.value.payments.postponed?.count || 0)
	);
});

const vehicleLabel = computed(() => {
	if (!ctx.value?.vehicle) return "—";
	const v = ctx.value.vehicle;
	return (
		[v.make, v.model].filter(Boolean).join(" ") || v.license_plate || "Vehicle"
	);
});

const vehicleStatusClass = computed(() => {
	const status = ctx.value?.vehicle?.vehicle_status;
	if (!status) return "bg-gray-100 text-gray-600";
	const map = {
		Available: "bg-emerald-100 text-emerald-700",
		Rented: "bg-blue-100 text-blue-700",
		"Owned by Client": "bg-gray-200 text-gray-600",
		Maintenance: "bg-amber-100 text-amber-700",
	};
	return map[status] ?? "bg-blue-100 text-blue-700";
});

function formatCurrency(value) {
	if (value == null) return "—";
	return new Intl.NumberFormat("en-US", {
		minimumFractionDigits: 0,
		maximumFractionDigits: 0,
	}).format(value);
}

const detail = reactive({
	open: false,
	type: "",
	title: "",
	icon: "",
	iconBg: "",
	rows: [],
});

const DETAIL_CONFIG = {
	paid: {
		title: "Paid Payments",
		icon: "✅",
		iconBg: "bg-emerald-50",
		rowsKey: "paid",
	},
	invoiced: {
		title: "Pending Payments",
		icon: "🕐",
		iconBg: "bg-amber-50",
		rowsKey: "invoiced",
	},
	postponed: {
		title: "Postponed Payments",
		icon: "⏸️",
		iconBg: "bg-red-50",
		rowsKey: "postponed",
	},
};

function openDetail(type) {
	const cfg = DETAIL_CONFIG[type];
	if (!cfg || !ctx.value) return;
	detail.type = type;
	detail.title = cfg.title;
	detail.icon = cfg.icon;
	detail.iconBg = cfg.iconBg;
	detail.rows = ctx.value.payments[cfg.rowsKey]?.rows ?? [];
	detail.open = true;
}

async function logout() {
	await session.logout();
}
</script>

<style scoped>
.drawer-enter-active,
.drawer-leave-active {
	transition: opacity 0.25s ease;
}
.drawer-enter-from,
.drawer-leave-to {
	opacity: 0;
}

.drawer-enter-active .relative,
.drawer-leave-active .relative {
	transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}
.drawer-enter-from .relative,
.drawer-leave-to .relative {
	transform: translateY(100%);
}
@media (min-width: 640px) {
	.drawer-enter-from .relative,
	.drawer-leave-to .relative {
		transform: scale(0.96) translateY(8px);
	}
}
</style>
