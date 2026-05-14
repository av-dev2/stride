import path from "path";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig(async ({ mode }) => {
	const isDev = mode === "development";

	const config = {
		plugins: [vue()],
		server: {
			port: 8080,
			host: "0.0.0.0",
			allowedHosts: true,
		},
		resolve: {
			alias: {
				"@": path.resolve(__dirname, "src"),
			},
		},
		optimizeDeps: {
			include: [
				"feather-icons",
				"showdown",
				"engine.io-client",
				"socket.io-client",
			],
		},
		build: {
			outDir: "../stride/public/frontend",
			emptyOutDir: true,
			target: "es2015",
		},
	};

	// Import the frappe-ui vite plugin for icons, proxy, etc.
	const frappeui = await importFrappeUIPlugin(isDev, config);
	config.plugins.unshift(
		frappeui({
			frappeProxy: true,
			lucideIcons: true,
			jinjaBootData: true,
			buildConfig: {
				indexHtmlPath: "../stride/www/frontend.html",
				emptyOutDir: true,
				sourcemap: true,
			},
		})
	);

	return config;
});

async function importFrappeUIPlugin(isDev, config) {
	if (isDev) {
		try {
			const fs = await import("node:fs");
			const localVitePluginPath = path.resolve(__dirname, "../frappe-ui/vite");
			if (fs.existsSync(localVitePluginPath)) {
				const module = await import("../frappe-ui/vite");
				console.info("Local frappe-ui vite plugin found, using local plugin");
				return module.default;
			}
		} catch {
			// fall through to npm package
		}
	}
	const module = await import("frappe-ui/vite");
	return module.default;
}
