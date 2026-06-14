import "./style.css";
import "leaflet/dist/leaflet.css";

import { createApp } from "vue";
import {
	FrappeUI,
	Button,
	Badge,
	setConfig,
	frappeRequest,
	FeatherIcon,
} from "frappe-ui";
import router from "./router";
import App from "./App.vue";
import { session } from "./data/session";

const app = createApp(App);

setConfig("resourceFetcher", frappeRequest);

app.use(FrappeUI);
app.use(router);

// Register global components
app.component("Button", Button);
app.component("Badge", Badge);
app.component("FeatherIcon", FeatherIcon);

// Provide session globally so all views can inject("$session")
app.provide("$session", session);

// Register service worker (production only)
if ("serviceWorker" in navigator && import.meta.env.PROD) {
	navigator.serviceWorker
		.register("/assets/stride/frontend/sw.js", { type: "classic" })
		.then(() => console.log("[Stride] Service worker registered."))
		.catch((err) =>
			console.error("[Stride] Service worker registration failed:", err)
		);
}

if (import.meta.env.DEV) {
	frappeRequest({
		url: "/api/method/stride.www.frontend.get_context_for_dev",
	}).then((values) => {
		for (let key in values) {
			window[key] = values[key];
		}
		app.mount("#app");
	});
} else {
	app.mount("#app");
}
