import { createRouter, createWebHistory } from "vue-router";
import { session } from "../data/session";

const routes = [
	{
		path: "/",
		name: "Home",
		component: () => import("../views/Home.vue"),
	},
	{
		path: "/login",
		name: "Login",
		component: () => import("../views/Login.vue"),
		meta: { isGuestRoute: true },
	},
	{
		path: "/vehicle-map",
		name: "VehicleMap",
		component: () => import("../views/VehicleMap.vue"),
	},
	{
		path: "/vehicles",
		name: "VehicleList",
		component: () => import("../views/VehicleList.vue"),
	},
	{
		path: "/vehicles/:vehicle",
		name: "VehicleDetail",
		component: () => import("../views/VehicleDetail.vue"),
		props: true,
	},
];

const router = createRouter({
	history: createWebHistory("/frontend"),
	routes,
});

// Navigation guard
router.beforeEach((to, _from, next) => {
	const isLoggedIn = session.isLoggedIn;

	// If not logged in and trying to access a protected route → go to /login
	if (!isLoggedIn && !to.meta?.isGuestRoute) {
		return next({ name: "Login" });
	}

	// If already logged in and trying to visit /login → redirect to Home
	if (isLoggedIn && to.name === "Login") {
		return next({ name: "Home" });
	}

	next();
});

export default router;
