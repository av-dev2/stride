/**
 * Check if the current user is logged in by reading the session cookie.
 * Returns the user_id if logged in, or null if guest/unauthenticated.
 */
export function sessionUser() {
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"));
	const userId = cookies.get("user_id");
	if (!userId || userId === "Guest") {
		return null;
	}
	return userId;
}

/**
 * Vue Router navigation guard.
 * Redirects unauthenticated users to Frappe's login page.
 */
export function authGuard(to, from, next) {
	const user = sessionUser();

	if (!user && !to.meta?.isGuestRoute) {
		// Redirect to Frappe's built-in login, with redirect back to this SPA
		window.location.href = `/login?redirect-to=/frontend${to.fullPath}`;
		return;
	}

	next();
}
