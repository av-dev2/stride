<template>
	<div class="min-h-screen bg-gray-50 p-6">
		<div class="max-w-4xl mx-auto">
			<h1 class="text-2xl font-bold text-gray-900 mb-6">Stride</h1>
			<p class="text-gray-600 mb-8">Vehicle Rental Management</p>

			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				<router-link
					to="/vehicle-map"
					class="block p-6 bg-white rounded-xl border border-gray-200 hover:shadow-md transition-shadow"
				>
					<div class="flex items-center gap-3 mb-2">
						<FeatherIcon name="map-pin" class="w-6 h-6 text-blue-500" />
						<h2 class="text-lg font-semibold text-gray-900">Vehicle Map</h2>
					</div>
					<p class="text-sm text-gray-500">
						Live GPS tracking of your fleet on an interactive map
					</p>
				</router-link>
			</div>
		</div>
	</div>
</template>

<script setup></script>
