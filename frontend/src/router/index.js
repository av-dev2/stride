import { createRouter, createWebHistory } from "vue-router";
import { authGuard } from "./auth";

const routes = [
	{
		path: "/",
		name: "Home",
		component: () => import("../views/Home.vue"),
	},
	{
		path: "/vehicle-map",
		name: "VehicleMap",
		component: () => import("../views/VehicleMap.vue"),
	},
];

const router = createRouter({
	history: createWebHistory("/frontend"),
	routes,
});

// Protect all routes — redirect to /login if not authenticated
router.beforeEach(authGuard);

export default router;
