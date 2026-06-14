import { computed, reactive } from "vue";
import { call } from "frappe-ui";
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

function handleLoginResponse(response) {
	if (response.message === "Logged In") {
		session.user = sessionUser();
		router.replace({ name: "Home" });
	}
}

export const session = reactive({
	user: sessionUser(),
	isLoggedIn: computed(() => !!session.user),

	/** Log in with email + password. Returns the raw Frappe response. */
	login: async (email, password) => {
		const response = await call("login", { usr: email, pwd: password });
		handleLoginResponse(response);
		return response;
	},

	/** Log out and redirect to the login page. */
	logout: async () => {
		await call("logout");
		session.user = null;
		// Full reload so cookies are cleared cleanly
		window.location.href = "/frontend/login";
	},
});
