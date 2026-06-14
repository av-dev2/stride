<template>
	<div
		class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4"
	>
		<div class="w-full max-w-sm">
			<!-- Logo / Brand -->
			<div class="text-center mb-10">
				<div
					class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-blue-600 shadow-lg shadow-blue-200 mb-4"
				>
					<svg
						class="w-9 h-9 text-white"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
						stroke-width="1.8"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
						/>
					</svg>
				</div>
				<h1 class="text-2xl font-bold text-gray-900 tracking-tight">Stride</h1>
				<p class="text-sm text-gray-500 mt-1">Vehicle Rental Portal</p>
			</div>

			<!-- Card -->
			<div
				class="bg-white rounded-2xl shadow-xl shadow-gray-100/80 border border-gray-100 p-8"
			>
				<h2 class="text-lg font-semibold text-gray-800 mb-6">
					Sign in to your account
				</h2>

				<form @submit.prevent="submit" class="space-y-4" novalidate>
					<!-- Email -->
					<div>
						<label
							for="stride-email"
							class="block text-sm font-medium text-gray-700 mb-1.5"
							>Email</label
						>
						<input
							id="stride-email"
							v-model="email"
							type="email"
							autocomplete="username"
							placeholder="you@example.com"
							required
							class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 text-gray-900 text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
						/>
					</div>

					<!-- Password -->
					<div>
						<label
							for="stride-password"
							class="block text-sm font-medium text-gray-700 mb-1.5"
							>Password</label
						>
						<input
							id="stride-password"
							v-model="password"
							type="password"
							autocomplete="current-password"
							placeholder="••••••••"
							required
							class="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 text-gray-900 text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
						/>
					</div>

					<!-- Error -->
					<div
						v-if="errorMessage"
						class="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg"
					>
						<svg
							class="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0"
							fill="currentColor"
							viewBox="0 0 20 20"
						>
							<path
								fill-rule="evenodd"
								d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
								clip-rule="evenodd"
							/>
						</svg>
						<p class="text-sm text-red-700">{{ errorMessage }}</p>
					</div>

					<!-- Submit -->
					<button
						id="stride-login-btn"
						type="submit"
						:disabled="loading"
						class="w-full mt-2 py-2.5 px-4 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 disabled:bg-blue-400 text-white text-sm font-semibold rounded-lg shadow-sm shadow-blue-200 transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 flex items-center justify-center gap-2"
					>
						<svg
							v-if="loading"
							class="animate-spin w-4 h-4"
							fill="none"
							viewBox="0 0 24 24"
						>
							<circle
								class="opacity-25"
								cx="12"
								cy="12"
								r="10"
								stroke="currentColor"
								stroke-width="4"
							/>
							<path
								class="opacity-75"
								fill="currentColor"
								d="M4 12a8 8 0 018-8v8z"
							/>
						</svg>
						<span>{{ loading ? "Signing in…" : "Sign In" }}</span>
					</button>
				</form>
			</div>

			<p class="text-center text-xs text-gray-400 mt-6">
				Powered by Stride Vehicle Rental Management
			</p>
		</div>
	</div>
</template>

<script setup>
import { ref, inject } from "vue";

const session = inject("$session");

const email = ref("");
const password = ref("");
const loading = ref(false);
const errorMessage = ref("");

async function submit() {
	if (!email.value || !password.value) {
		errorMessage.value = "Please enter your email and password.";
		return;
	}

	loading.value = true;
	errorMessage.value = "";

	try {
		await session.login(email.value, password.value);
	} catch (err) {
		const messages = err?.messages || err?.message;
		errorMessage.value =
			typeof messages === "string"
				? messages
				: Array.isArray(messages)
				? messages.join(" ")
				: "Login failed. Please check your credentials and try again.";
	} finally {
		loading.value = false;
	}
}
</script>
