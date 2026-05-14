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

const app = createApp(App);

setConfig("resourceFetcher", frappeRequest);

app.use(FrappeUI);
app.use(router);

// Register global components
app.component("Button", Button);
app.component("Badge", Badge);
app.component("FeatherIcon", FeatherIcon);

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
