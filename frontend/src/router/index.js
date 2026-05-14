import { createRouter, createWebHistory } from "vue-router";

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

export default router;
