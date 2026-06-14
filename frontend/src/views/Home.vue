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
					<div
						class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shadow-sm"
					>
						<svg
							class="w-5 h-5 text-white"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
							stroke-width="2"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 00-3.213-9.193 2.056 2.056 0 00-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 00-10.026 0 1.106 1.106 0 00-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12"
							/>
						</svg>
					</div>
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
						<svg
							class="w-4 h-4"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
							stroke-width="2"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
							/>
						</svg>
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

			<!-- Error / no customer -->
			<div
				v-else-if="ctx?.error"
				class="bg-amber-50 border border-amber-200 rounded-2xl p-6 text-center"
			>
				<svg
					class="w-10 h-10 text-amber-400 mx-auto mb-3"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 9v2m0 4h.01M21 12A9 9 0 113 12a9 9 0 0118 0z"
					/>
				</svg>
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
						<svg
							class="w-3.5 h-3.5"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
							stroke-width="2"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
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
					<div class="grid grid-cols-3 gap-3">
						<!-- Paid -->
						<button
							id="stride-card-paid"
							@click="openDetail('paid')"
							class="group bg-white rounded-2xl p-4 border border-gray-100 shadow-sm hover:shadow-md hover:border-emerald-200 transition-all duration-200 text-left"
						>
							<div
								class="w-9 h-9 rounded-xl bg-emerald-50 group-hover:bg-emerald-100 flex items-center justify-center mb-3 transition-colors"
							>
								<svg
									class="w-5 h-5 text-emerald-600"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
									stroke-width="2"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
									/>
								</svg>
							</div>
							<p class="text-2xl font-bold text-gray-900 leading-none">
								{{ ctx.payments.paid.count }}
							</p>
							<p class="text-xs text-gray-500 mt-1 font-medium">Paid</p>
						</button>

						<!-- Pending (Invoiced) -->
						<button
							id="stride-card-pending"
							@click="openDetail('invoiced')"
							class="group bg-white rounded-2xl p-4 border border-gray-100 shadow-sm hover:shadow-md hover:border-amber-200 transition-all duration-200 text-left"
						>
							<div
								class="w-9 h-9 rounded-xl bg-amber-50 group-hover:bg-amber-100 flex items-center justify-center mb-3 transition-colors"
							>
								<svg
									class="w-5 h-5 text-amber-600"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
									stroke-width="2"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
									/>
								</svg>
							</div>
							<p class="text-2xl font-bold text-gray-900 leading-none">
								{{ ctx.payments.invoiced.count }}
							</p>
							<p class="text-xs text-gray-500 mt-1 font-medium">Pending</p>
						</button>

						<!-- Postponed -->
						<button
							id="stride-card-postponed"
							@click="openDetail('postponed')"
							class="group bg-white rounded-2xl p-4 border border-gray-100 shadow-sm hover:shadow-md hover:border-red-200 transition-all duration-200 text-left"
						>
							<div
								class="w-9 h-9 rounded-xl bg-red-50 group-hover:bg-red-100 flex items-center justify-center mb-3 transition-colors"
							>
								<svg
									class="w-5 h-5 text-red-500"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
									stroke-width="2"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5"
									/>
								</svg>
							</div>
							<p class="text-2xl font-bold text-gray-900 leading-none">
								{{ ctx.payments.postponed.count }}
							</p>
							<p class="text-xs text-gray-500 mt-1 font-medium">Postponed</p>
						</button>
					</div>
				</section>

				<!-- ── Vehicle Detail Card ────────────────────────── -->
				<section v-if="ctx.vehicle">
					<h2
						class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3 px-1"
					>
						Your Vehicle
					</h2>
					<div
						class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden"
					>
						<!-- Vehicle image banner -->
						<div
							class="h-32 bg-gradient-to-r from-slate-700 to-slate-900 flex items-center justify-center relative overflow-hidden"
						>
							<img
								v-if="ctx.vehicle.vehicle_image"
								:src="ctx.vehicle.vehicle_image"
								:alt="vehicleLabel"
								class="object-cover w-full h-full opacity-80"
							/>
							<div v-else class="text-center text-slate-400">
								<svg
									class="w-14 h-14 mx-auto mb-1 opacity-50"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="1.2"
										d="M9 17a2 2 0 11-4 0 2 2 0 014 0zm10 0a2 2 0 11-4 0 2 2 0 014 0zM3 11l1.26-5.26A2 2 0 016.22 4h11.56a2 2 0 011.96 1.74L21 11M3 11h18M3 11l-.5 3H21.5L21 11"
									/>
								</svg>
							</div>
							<!-- Status badge -->
							<span
								class="absolute top-3 right-3 text-xs font-semibold px-2.5 py-1 rounded-full"
								:class="vehicleStatusClass"
							>
								{{ ctx.vehicle.vehicle_status || "—" }}
							</span>
						</div>

						<div class="p-4 space-y-3">
							<div>
								<p class="text-lg font-bold text-gray-900">
									{{ vehicleLabel }}
								</p>
								<p class="text-sm text-blue-600 font-semibold tracking-wider">
									{{ ctx.vehicle.license_plate }}
								</p>
							</div>

							<div class="grid grid-cols-3 gap-3">
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

							<!-- Lease summary strip -->
							<div
								class="bg-gray-50 rounded-xl p-3 grid grid-cols-2 gap-3 text-sm mt-1"
							>
								<div>
									<p class="text-xs text-gray-400 font-medium">Rate</p>
									<p class="font-semibold text-gray-800">
										{{ formatCurrency(ctx.lease.rate) }} /
										{{ ctx.lease.period_type }}
									</p>
								</div>
								<div>
									<p class="text-xs text-gray-400 font-medium">
										Contract Start
									</p>
									<p class="font-semibold text-gray-800">
										{{ ctx.lease.start_date }}
									</p>
								</div>
								<div>
									<p class="text-xs text-gray-400 font-medium">Contract End</p>
									<p class="font-semibold text-gray-800">
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
				<!-- Backdrop -->
				<div
					class="absolute inset-0 bg-black/40 backdrop-blur-sm"
					@click="detail.open = false"
				/>

				<!-- Sheet -->
				<div
					class="relative w-full max-w-lg bg-white rounded-t-3xl sm:rounded-2xl shadow-2xl max-h-[85vh] flex flex-col"
				>
					<!-- Header -->
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
							<svg
								class="w-4 h-4"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
								stroke-width="2.5"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
					</div>

					<!-- Rows -->
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
									<!-- Date display based on type -->
									<p class="text-sm font-semibold text-gray-800 mt-0.5">
										<template v-if="detail.type === 'paid'">
											{{ row.from_date }} → {{ row.to_date }}
										</template>
										<template v-else>
											{{ row.due_date }}
										</template>
									</p>
								</div>
								<span class="text-sm font-bold text-gray-900">{{
									formatCurrency(row.amount)
								}}</span>
							</div>

							<!-- Paid: show payment entry ref -->
							<div
								v-if="detail.type === 'paid' && row.payment_entry"
								class="flex items-center gap-1.5 mt-1"
							>
								<svg
									class="w-3 h-3 text-emerald-500 flex-shrink-0"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
									stroke-width="2"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="M9 12l2 2 4-4"
									/>
								</svg>
								<span class="text-xs text-gray-500">{{
									row.payment_entry
								}}</span>
							</div>

							<!-- Invoiced/Pending: show sales invoice ref -->
							<div
								v-if="detail.type === 'invoiced' && row.sales_invoice"
								class="flex items-center gap-1.5 mt-1"
							>
								<svg
									class="w-3 h-3 text-amber-500 flex-shrink-0"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
									stroke-width="2"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
									/>
								</svg>
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

const session = inject("$session");

// ── Data fetching ────────────────────────────────────────────────
const loading = ref(true);
const ctx = ref(null);

const pwaResource = createResource({
	url: "stride.api.pwa.get_pwa_context",
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

onMounted(() => pwaResource.fetch());

// ── Vehicle helpers ──────────────────────────────────────────────
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
		Active: "bg-emerald-100 text-emerald-700",
		"Out of Order": "bg-red-100 text-red-700",
		Scrapped: "bg-gray-200 text-gray-600",
	};
	return map[status] ?? "bg-blue-100 text-blue-700";
});

// ── Currency formatter ───────────────────────────────────────────
function formatCurrency(value) {
	if (value == null) return "—";
	return new Intl.NumberFormat("en-US", {
		minimumFractionDigits: 0,
		maximumFractionDigits: 0,
	}).format(value);
}

// ── Detail drawer ────────────────────────────────────────────────
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

// ── Logout ───────────────────────────────────────────────────────
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
