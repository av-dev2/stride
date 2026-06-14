import { cleanupOutdatedCaches, precacheAndRoute } from "workbox-precaching";
import { clientsClaim } from "workbox-core";

// Precache all assets injected by vite-plugin-pwa at build time
precacheAndRoute(self.__WB_MANIFEST);

// Clean up any caches from older versions
cleanupOutdatedCaches();

// Take control of all clients immediately on activation
self.skipWaiting();
clientsClaim();
