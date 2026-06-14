<template>
	<div id="stride-app" class="min-h-screen bg-gray-50">
		<router-view />

		<!-- PWA Install Banner -->
		<Transition name="slide-up">
			<div
				v-if="showInstallBanner"
				class="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:max-w-sm bg-white/95 backdrop-blur border border-blue-50 shadow-2xl rounded-2xl p-4 z-50 space-y-3"
			>
				<!-- Main Prompt View -->
				<template v-if="!showInstructions">
					<div class="flex items-start justify-between">
						<div class="flex items-center gap-3">
							<div
								class="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-md shadow-blue-200"
							>
								<!-- Stride Logo/Icon -->
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
								<h3 class="font-bold text-gray-900 text-sm">
									Download Stride PWA
								</h3>
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
						Install the Stride application on your device for quick offline
						access and a faster, native app experience.
					</p>
					<div class="flex gap-2">
						<button
							@click="dismissInstall"
							class="flex-1 py-2 text-xs font-semibold text-gray-600 bg-gray-50 border border-gray-100 rounded-lg hover:bg-gray-100 transition-colors"
						>
							Not Now
						</button>
						<button
							@click="handleInstallClick"
							class="flex-1 py-2 text-xs font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 shadow-sm shadow-blue-200 transition-colors"
						>
							Download App
						</button>
					</div>
				</template>

				<!-- Step-by-Step Instructions View -->
				<template v-else>
					<div
						class="flex items-center justify-between border-b border-gray-100 pb-2"
					>
						<button
							@click="showInstructions = false"
							class="flex items-center gap-1 text-xs text-blue-600 font-semibold hover:text-blue-700 transition-colors"
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
									d="M15.75 19.5L8.25 12l7.5-7.5"
								/>
							</svg>
							Back
						</button>
						<span class="text-xs font-bold text-gray-900">How to Install</span>
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

					<div class="space-y-3 pt-1">
						<p class="text-[11px] text-gray-500">
							Follow these quick steps to add Stride to your device:
						</p>

						<!-- iOS / Safari Instructions -->
						<div v-if="deviceOS === 'ios'" class="space-y-2.5">
							<div class="flex items-start gap-2.5 text-xs text-gray-700">
								<span
									class="flex items-center justify-center w-5 h-5 rounded-full bg-blue-50 text-blue-600 text-[10px] font-bold shrink-0"
									>1</span
								>
								<p class="leading-relaxed">
									Tap the
									<span class="font-semibold text-gray-900">Share</span> button
									<span
										class="inline-flex items-center justify-center bg-gray-100 p-0.5 rounded text-gray-700 ml-0.5 align-middle"
									>
										<svg
											class="w-3 h-3"
											fill="none"
											viewBox="0 0 24 24"
											stroke="currentColor"
											stroke-width="2"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												d="M9 8.25H7.5a2.25 2.25 0 00-2.25 2.25v9a2.25 2.25 0 002.25 2.25h9a2.25 2.25 0 002.25-2.25v-9a2.25 2.25 0 00-2.25-2.25H15M9 12l3-3m0 0l3 3m-3-3V2.25"
											/>
										</svg>
									</span>
									in Safari.
								</p>
							</div>
							<div class="flex items-start gap-2.5 text-xs text-gray-700">
								<span
									class="flex items-center justify-center w-5 h-5 rounded-full bg-blue-50 text-blue-600 text-[10px] font-bold shrink-0"
									>2</span
								>
								<p class="leading-relaxed">
									Scroll down and tap
									<span class="font-semibold text-gray-900"
										>Add to Home Screen</span
									>
									<span
										class="inline-flex items-center justify-center bg-gray-100 p-0.5 rounded text-gray-700 ml-0.5 align-middle"
									>
										<svg
											class="w-3 h-3"
											fill="none"
											viewBox="0 0 24 24"
											stroke="currentColor"
											stroke-width="2"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												d="M12 4.5v15m7.5-7.5h-15"
											/>
										</svg> </span
									>.
								</p>
							</div>
						</div>

						<!-- Android / Chrome Instructions -->
						<div v-else-if="deviceOS === 'android'" class="space-y-2.5">
							<div class="flex items-start gap-2.5 text-xs text-gray-700">
								<span
									class="flex items-center justify-center w-5 h-5 rounded-full bg-blue-50 text-blue-600 text-[10px] font-bold shrink-0"
									>1</span
								>
								<p class="leading-relaxed">
									Tap the browser
									<span class="font-semibold text-gray-900">Menu</span> button
									<span
										class="inline-flex items-center justify-center bg-gray-100 p-0.5 rounded text-gray-700 ml-0.5 align-middle"
									>
										<svg
											class="w-3 h-3"
											fill="currentColor"
											viewBox="0 0 24 24"
										>
											<circle cx="12" cy="5" r="2" />
											<circle cx="12" cy="12" r="2" />
											<circle cx="12" cy="19" r="2" />
										</svg>
									</span>
									in the top-right.
								</p>
							</div>
							<div class="flex items-start gap-2.5 text-xs text-gray-700">
								<span
									class="flex items-center justify-center w-5 h-5 rounded-full bg-blue-50 text-blue-600 text-[10px] font-bold shrink-0"
									>2</span
								>
								<p class="leading-relaxed">
									Tap
									<span class="font-semibold text-gray-900"
										>Add to Home screen</span
									>
									or
									<span class="font-semibold text-gray-900">Install app</span>.
								</p>
							</div>
						</div>

						<!-- Desktop Instructions -->
						<div v-else class="space-y-2.5">
							<div class="flex items-start gap-2.5 text-xs text-gray-700">
								<span
									class="flex items-center justify-center w-5 h-5 rounded-full bg-blue-50 text-blue-600 text-[10px] font-bold shrink-0"
									>1</span
								>
								<p class="leading-relaxed">
									Click the **Install** button
									<span
										class="inline-flex items-center justify-center bg-blue-50 p-0.5 rounded text-blue-600 ml-0.5 align-middle"
									>
										<svg
											class="w-3 h-3"
											fill="none"
											viewBox="0 0 24 24"
											stroke="currentColor"
											stroke-width="2"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
											/>
										</svg>
									</span>
									in the address bar.
								</p>
							</div>
							<div class="flex items-start gap-2.5 text-xs text-gray-700">
								<span
									class="flex items-center justify-center w-5 h-5 rounded-full bg-blue-50 text-blue-600 text-[10px] font-bold shrink-0"
									>2</span
								>
								<p class="leading-relaxed">
									Or click the menu button (three dots) and select
									<span class="font-semibold text-gray-900"
										>Save and share</span
									>
									>
									<span class="font-semibold text-gray-900">Install page</span>.
								</p>
							</div>
						</div>

						<button
							@click="dismissInstall"
							class="w-full py-1.5 mt-1 text-center text-xs font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
						>
							Got It
						</button>
					</div>
				</template>
			</div>
		</Transition>
	</div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const deferredPrompt = ref(null);
const showInstallBanner = ref(false);
const showInstructions = ref(false);
const deviceOS = ref("desktop");

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

const handleInstallClick = async () => {
	if (deferredPrompt.value) {
		// Trigger the browser installation prompt
		deferredPrompt.value.prompt();
		// Await user's response
		const { outcome } = await deferredPrompt.value.userChoice;
		console.log(`PWA installation outcome: ${outcome}`);
		// Reset the stashed event
		deferredPrompt.value = null;
		showInstallBanner.value = false;
	} else {
		// Fallback: show instructions
		showInstructions.value = true;
	}
};

const dismissInstall = () => {
	showInstallBanner.value = false;
	localStorage.setItem("stride-pwa-dismissed", "true");
};

// Check OS / Device type
const detectDevice = () => {
	const ua = navigator.userAgent;
	if (/iPhone|iPad|iPod/i.test(ua)) {
		deviceOS.value = "ios";
	} else if (/Android/i.test(ua)) {
		deviceOS.value = "android";
	} else {
		deviceOS.value = "desktop";
	}
};

onMounted(() => {
	window.addEventListener("beforeinstallprompt", handleInstallPrompt);
	detectDevice();

	// Check if already in standalone/installed mode
	const isStandalone =
		window.matchMedia("(display-mode: standalone)").matches ||
		(window.navigator && window.navigator.standalone === true);

	if (!isStandalone) {
		// If not in standalone mode, and not dismissed, show the prompt banner
		if (localStorage.getItem("stride-pwa-dismissed") !== "true") {
			// Show after a short delay for a smoother experience
			setTimeout(() => {
				showInstallBanner.value = true;
			}, 1500);
		}
	}
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
