<template>
	<div id="stride-app" class="min-h-screen bg-gray-50">
		<router-view />

		<!-- PWA Install Banner -->
		<Transition name="slide-up">
			<div
				v-if="showInstallBanner"
				class="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:max-w-sm bg-white/95 backdrop-blur border border-blue-50 shadow-2xl rounded-2xl p-4 z-50 space-y-3"
			>
				<div class="flex items-start justify-between">
					<div class="flex items-center gap-3">
						<div
							class="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-sm"
						>
							<svg
								class="w-6 h-6 text-white"
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
						<div>
							<h3 class="font-bold text-gray-900 text-sm">Install Stride</h3>
							<p class="text-[11px] text-gray-400">
								Stride Vehicle Rental Portal
							</p>
						</div>
					</div>
					<button
						@click="dismissInstall"
						class="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center text-gray-400 hover:bg-gray-200 transition-colors"
					>
						<svg
							class="w-3.5 h-3.5"
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
				<p class="text-xs text-gray-600 leading-normal">
					Add Stride to your home screen for offline access and a faster, native
					app experience.
				</p>
				<div class="flex gap-2">
					<button
						@click="dismissInstall"
						class="flex-1 py-2 text-xs font-semibold text-gray-600 bg-gray-50 border border-gray-100 rounded-lg hover:bg-gray-100 transition-colors"
					>
						Not Now
					</button>
					<button
						@click="installApp"
						class="flex-1 py-2 text-xs font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 shadow-sm shadow-blue-200 transition-colors"
					>
						Install App
					</button>
				</div>
			</div>
		</Transition>
	</div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const deferredPrompt = ref(null);
const showInstallBanner = ref(false);

const handleInstallPrompt = (e) => {
	// Prevent the default browser prompt banner
	e.preventDefault();
	// Save the event so it can be triggered later.
	deferredPrompt.value = e;
	// Only show the custom banner if the user hasn't dismissed it previously
	if (localStorage.getItem("stride-pwa-dismissed") !== "true") {
		showInstallBanner.value = true;
	}
};

const installApp = async () => {
	if (!deferredPrompt.value) return;
	// Trigger the browser installation prompt
	deferredPrompt.value.prompt();
	// Await user's response
	const { outcome } = await deferredPrompt.value.userChoice;
	console.log(`PWA installation outcome: ${outcome}`);
	// Reset the stashed event
	deferredPrompt.value = null;
	showInstallBanner.value = false;
};

const dismissInstall = () => {
	showInstallBanner.value = false;
	localStorage.setItem("stride-pwa-dismissed", "true");
};

onMounted(() => {
	window.addEventListener("beforeinstallprompt", handleInstallPrompt);
});

onUnmounted(() => {
	window.removeEventListener("beforeinstallprompt", handleInstallPrompt);
});
</script>

<style scoped>
.slide-up-enter-active,
.slide-up-leave-active {
	transition: all 0.3s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
	transform: translateY(100px);
	opacity: 0;
}
</style>
