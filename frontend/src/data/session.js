import { computed, reactive } from "vue";
import router from "@/router";

/**
 * Read the logged-in user from the Frappe session cookie.
 * Returns null if the user is a Guest or the cookie is missing.
 */
export function sessionUser() {
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"));
	const userId = cookies.get("user_id");
	return !userId || userId === "Guest" ? null : userId;
}

export const session = reactive({
	user: sessionUser(),
	isLoggedIn: computed(() => !!session.user),

	/** Log in with email + password via a direct POST to Frappe's login endpoint. */
	login: async (email, password) => {
		const csrfToken = window.csrf_token || window.boot?.csrf_token || "fetch";

		const response = await fetch("/api/method/login", {
			method: "POST",
			headers: {
				"Content-Type": "application/json; charset=utf-8",
				Accept: "application/json",
				"X-Frappe-Site-Name": window.location.hostname,
				"X-Frappe-CSRF-Token": csrfToken,
			},
			body: JSON.stringify({ usr: email, pwd: password }),
		});

		const data = await response.json();

		if (!response.ok) {
			// Build a readable error from Frappe's error shape
			let messages = [];
			if (data._server_messages) {
				try {
					messages = JSON.parse(data._server_messages).map((m) => {
						try {
							return JSON.parse(m).message;
						} catch {
							return m;
						}
					});
				} catch {
					/* ignore */
				}
			}
			if (!messages.length && data.message) messages = [data.message];
			if (!messages.length && data._error_message)
				messages = [data._error_message];
			throw new Error(messages.join(" ") || "Invalid email or password.");
		}

		if (data.message === "Logged In") {
			session.user = sessionUser();
			router.replace({ name: "Home" });
		}

		return data;
	},

	/** Log out and redirect to the login page. */
	logout: async () => {
		await fetch("/api/method/logout", { method: "POST" });
		session.user = null;
		window.location.href = "/frontend/login";
	},
});
