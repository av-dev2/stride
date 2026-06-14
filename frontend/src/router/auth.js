/**
 * Read the Frappe session user from the browser cookie.
 * Kept for backward-compatibility; the main guard now lives in router/index.js.
 */
export function sessionUser() {
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"));
	const userId = cookies.get("user_id");
	return !userId || userId === "Guest" ? null : userId;
}
