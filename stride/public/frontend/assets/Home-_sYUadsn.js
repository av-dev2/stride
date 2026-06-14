import {
	E as e,
	F as t,
	J as n,
	L as r,
	M as i,
	_ as a,
	b as o,
	g as s,
	gt as c,
	m as l,
	p as u,
	pt as d,
	r as ee,
	rt as f,
	t as p,
	tt as m,
	u as h,
	x as te,
	y as ne,
} from "./asyncToGenerator-COJlnFvb.js";
import { t as re } from "./_plugin-vue_export-helper-DOrAluW7.js";
import { r as ie } from "./index-lXaXi-wZ.js";
var ae = {
		class: `min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/40`,
	},
	oe = {
		class: `bg-white/80 backdrop-blur border-b border-gray-100 sticky top-0 z-30`,
	},
	se = {
		class: `max-w-2xl mx-auto px-4 h-14 flex items-center justify-between`,
	},
	ce = { class: `flex items-center gap-3` },
	g = { key: 0, class: `text-sm text-gray-600 font-medium hidden sm:inline` },
	_ = { class: `max-w-2xl mx-auto px-4 py-6 space-y-6` },
	v = { key: 0, class: `space-y-4` },
	y = {
		key: 1,
		class: `bg-amber-50 border border-amber-200 rounded-2xl p-6 text-center`,
	},
	b = { class: `text-amber-800 font-medium` },
	x = {
		class: `bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-5 text-white shadow-lg shadow-blue-200/50`,
	},
	S = { class: `text-xl font-bold tracking-tight` },
	C = { class: `mt-3 flex items-center gap-2 text-blue-100 text-xs` },
	w = { class: `grid grid-cols-3 gap-3` },
	T = { class: `text-2xl font-bold text-gray-900 leading-none` },
	E = { class: `text-2xl font-bold text-gray-900 leading-none` },
	D = { class: `text-2xl font-bold text-gray-900 leading-none` },
	O = { key: 0 },
	k = {
		class: `bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden`,
	},
	A = {
		class: `h-32 bg-gradient-to-r from-slate-700 to-slate-900 flex items-center justify-center relative overflow-hidden`,
	},
	j = [`src`, `alt`],
	M = { key: 1, class: `text-center text-slate-400` },
	N = { class: `p-4 space-y-3` },
	P = { class: `text-lg font-bold text-gray-900` },
	F = { class: `text-sm text-blue-600 font-semibold tracking-wider` },
	I = { class: `grid grid-cols-3 gap-3` },
	L = { class: `text-center` },
	R = { class: `text-sm font-semibold text-gray-800 mt-0.5` },
	z = { class: `text-center` },
	B = { class: `text-sm font-semibold text-gray-800 mt-0.5` },
	V = { class: `text-center` },
	H = { class: `text-sm font-semibold text-gray-800 mt-0.5` },
	U = {
		class: `bg-gray-50 rounded-xl p-3 grid grid-cols-2 gap-3 text-sm mt-1`,
	},
	le = { class: `font-semibold text-gray-800` },
	W = { class: `font-semibold text-gray-800` },
	ue = { class: `font-semibold text-emerald-600` },
	de = { class: `font-semibold text-red-500` },
	fe = {
		key: 0,
		class: `fixed inset-0 z-50 flex items-end sm:items-center justify-center`,
	},
	pe = {
		class: `relative w-full max-w-lg bg-white rounded-t-3xl sm:rounded-2xl shadow-2xl max-h-[85vh] flex flex-col`,
	},
	me = {
		class: `flex items-center justify-between px-5 pt-5 pb-4 border-b border-gray-100 flex-shrink-0`,
	},
	he = { class: `flex items-center gap-3` },
	ge = { class: `text-lg` },
	_e = { class: `font-bold text-gray-900 text-base leading-tight` },
	ve = { class: `text-xs text-gray-400` },
	ye = { class: `overflow-y-auto flex-1 px-4 py-3 space-y-2` },
	be = { class: `flex items-start justify-between mb-2` },
	xe = { class: `text-xs font-bold text-gray-400 uppercase tracking-wide` },
	Se = { class: `text-sm font-semibold text-gray-800 mt-0.5` },
	Ce = { class: `text-sm font-bold text-gray-900` },
	we = { key: 0, class: `flex items-center gap-1.5 mt-1` },
	Te = { class: `text-xs text-gray-500` },
	Ee = { key: 1, class: `flex items-center gap-1.5 mt-1` },
	De = { class: `text-xs text-gray-500` },
	Oe = { key: 0, class: `text-center py-10 text-gray-400` },
	G = re(
		{
			__name: `Home`,
			setup(re) {
				let G = e(`$session`),
					K = f(!0),
					q = f(null),
					J = ie({
						url: `stride.api.pwa.get_pwa_context`,
						method: `GET`,
						auto: !1,
						onSuccess(e) {
							(q.value = e), (K.value = !1);
						},
						onError() {
							K.value = !1;
						},
					});
				i(() => J.fetch());
				let Y = u(() => {
						var e;
						if (!((e = q.value) != null && e.vehicle)) return `—`;
						let t = q.value.vehicle;
						return (
							[t.make, t.model].filter(Boolean).join(` `) ||
							t.license_plate ||
							`Vehicle`
						);
					}),
					ke = u(() => {
						var e, t;
						let n =
							(e = q.value) == null || (e = e.vehicle) == null
								? void 0
								: e.vehicle_status;
						return n
							? (t = {
									Active: `bg-emerald-100 text-emerald-700`,
									"Out of Order": `bg-red-100 text-red-700`,
									Scrapped: `bg-gray-200 text-gray-600`,
							  }[n]) == null
								? `bg-blue-100 text-blue-700`
								: t
							: `bg-gray-100 text-gray-600`;
					});
				function X(e) {
					return e == null
						? `—`
						: new Intl.NumberFormat(`en-US`, {
								minimumFractionDigits: 0,
								maximumFractionDigits: 0,
						  }).format(e);
				}
				let Z = m({
						open: !1,
						type: ``,
						title: ``,
						icon: ``,
						iconBg: ``,
						rows: [],
					}),
					Ae = {
						paid: {
							title: `Paid Payments`,
							icon: `✅`,
							iconBg: `bg-emerald-50`,
							rowsKey: `paid`,
						},
						invoiced: {
							title: `Pending Payments`,
							icon: `🕐`,
							iconBg: `bg-amber-50`,
							rowsKey: `invoiced`,
						},
						postponed: {
							title: `Postponed Payments`,
							icon: `⏸️`,
							iconBg: `bg-red-50`,
							rowsKey: `postponed`,
						},
					};
				function Q(e) {
					var t, n;
					let r = Ae[e];
					!r ||
						!q.value ||
						((Z.type = e),
						(Z.title = r.title),
						(Z.icon = r.icon),
						(Z.iconBg = r.iconBg),
						(Z.rows =
							(t =
								(n = q.value.payments[r.rowsKey]) == null ? void 0 : n.rows) ==
							null
								? []
								: t),
						(Z.open = !0));
				}
				function je() {
					return $.apply(this, arguments);
				}
				function $() {
					return (
						($ = p(function* () {
							yield G.logout();
						})),
						$.apply(this, arguments)
					);
				}
				return (e, i) => {
					var u, f, p, m;
					return (
						t(),
						a(`div`, ae, [
							l(`header`, oe, [
								l(`div`, se, [
									i[6] ||
										(i[6] = ne(
											`<div class="flex items-center gap-2.5" data-v-22bccf86><div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shadow-sm" data-v-22bccf86><svg class="w-4.5 h-4.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" data-v-22bccf86><path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" data-v-22bccf86></path></svg></div><span class="font-bold text-gray-900 text-base tracking-tight" data-v-22bccf86>Stride</span></div>`,
											1
										)),
									l(`div`, ce, [
										(u = q.value) != null && u.customer_name
											? (t(), a(`span`, g, c(q.value.customer_name), 1))
											: s(``, !0),
										l(
											`button`,
											{
												id: `stride-logout-btn`,
												onClick: je,
												class: `flex items-center gap-1.5 text-sm text-gray-500 hover:text-red-600 transition-colors px-2 py-1 rounded-lg hover:bg-red-50`,
											},
											[
												...(i[5] ||
													(i[5] = [
														l(
															`svg`,
															{
																class: `w-4 h-4`,
																fill: `none`,
																viewBox: `0 0 24 24`,
																stroke: `currentColor`,
																"stroke-width": `2`,
															},
															[
																l(`path`, {
																	"stroke-linecap": `round`,
																	"stroke-linejoin": `round`,
																	d: `M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1`,
																}),
															],
															-1
														),
														l(
															`span`,
															{ class: `hidden sm:inline` },
															`Logout`,
															-1
														),
													])),
											]
										),
									]),
								]),
							]),
							l(`main`, _, [
								K.value
									? (t(),
									  a(`div`, v, [
											(t(),
											a(
												h,
												null,
												r(4, (e) =>
													l(`div`, {
														key: e,
														class: `bg-white rounded-2xl h-28 animate-pulse border border-gray-100`,
													})
												),
												64
											)),
									  ]))
									: (f = q.value) != null && f.error
									? (t(),
									  a(`div`, y, [
											i[7] ||
												(i[7] = l(
													`svg`,
													{
														class: `w-10 h-10 text-amber-400 mx-auto mb-3`,
														fill: `none`,
														viewBox: `0 0 24 24`,
														stroke: `currentColor`,
													},
													[
														l(`path`, {
															"stroke-linecap": `round`,
															"stroke-linejoin": `round`,
															"stroke-width": `2`,
															d: `M12 9v2m0 4h.01M21 12A9 9 0 113 12a9 9 0 0118 0z`,
														}),
													],
													-1
												)),
											l(`p`, b, c(q.value.message), 1),
									  ]))
									: q.value
									? (t(),
									  a(
											h,
											{ key: 2 },
											[
												l(`div`, x, [
													i[9] ||
														(i[9] = l(
															`p`,
															{
																class: `text-blue-100 text-sm font-medium mb-0.5`,
															},
															`Welcome back,`,
															-1
														)),
													l(`h1`, S, c(q.value.customer_name), 1),
													l(`div`, C, [
														i[8] ||
															(i[8] = l(
																`svg`,
																{
																	class: `w-3.5 h-3.5`,
																	fill: `none`,
																	viewBox: `0 0 24 24`,
																	stroke: `currentColor`,
																	"stroke-width": `2`,
																},
																[
																	l(`path`, {
																		"stroke-linecap": `round`,
																		"stroke-linejoin": `round`,
																		d: `M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z`,
																	}),
																],
																-1
															)),
														l(
															`span`,
															null,
															`Lease ` +
																c(
																	(p = q.value.lease) == null ? void 0 : p.name
																) +
																` · ` +
																c(
																	(m = q.value.lease) == null
																		? void 0
																		: m.status
																),
															1
														),
													]),
												]),
												l(`section`, null, [
													i[16] ||
														(i[16] = l(
															`h2`,
															{
																class: `text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3 px-1`,
															},
															`Payment Summary`,
															-1
														)),
													l(`div`, w, [
														l(
															`button`,
															{
																id: `stride-card-paid`,
																onClick: i[0] || (i[0] = (e) => Q(`paid`)),
																class: `group bg-white rounded-2xl p-4 border border-gray-100 shadow-sm hover:shadow-md hover:border-emerald-200 transition-all duration-200 text-left`,
															},
															[
																i[10] ||
																	(i[10] = l(
																		`div`,
																		{
																			class: `w-9 h-9 rounded-xl bg-emerald-50 group-hover:bg-emerald-100 flex items-center justify-center mb-3 transition-colors`,
																		},
																		[
																			l(
																				`svg`,
																				{
																					class: `w-5 h-5 text-emerald-600`,
																					fill: `none`,
																					viewBox: `0 0 24 24`,
																					stroke: `currentColor`,
																					"stroke-width": `2`,
																				},
																				[
																					l(`path`, {
																						"stroke-linecap": `round`,
																						"stroke-linejoin": `round`,
																						d: `M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z`,
																					}),
																				]
																			),
																		],
																		-1
																	)),
																l(`p`, T, c(q.value.payments.paid.count), 1),
																i[11] ||
																	(i[11] = l(
																		`p`,
																		{
																			class: `text-xs text-gray-500 mt-1 font-medium`,
																		},
																		`Paid`,
																		-1
																	)),
															]
														),
														l(
															`button`,
															{
																id: `stride-card-pending`,
																onClick: i[1] || (i[1] = (e) => Q(`invoiced`)),
																class: `group bg-white rounded-2xl p-4 border border-gray-100 shadow-sm hover:shadow-md hover:border-amber-200 transition-all duration-200 text-left`,
															},
															[
																i[12] ||
																	(i[12] = l(
																		`div`,
																		{
																			class: `w-9 h-9 rounded-xl bg-amber-50 group-hover:bg-amber-100 flex items-center justify-center mb-3 transition-colors`,
																		},
																		[
																			l(
																				`svg`,
																				{
																					class: `w-5 h-5 text-amber-600`,
																					fill: `none`,
																					viewBox: `0 0 24 24`,
																					stroke: `currentColor`,
																					"stroke-width": `2`,
																				},
																				[
																					l(`path`, {
																						"stroke-linecap": `round`,
																						"stroke-linejoin": `round`,
																						d: `M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z`,
																					}),
																				]
																			),
																		],
																		-1
																	)),
																l(
																	`p`,
																	E,
																	c(q.value.payments.invoiced.count),
																	1
																),
																i[13] ||
																	(i[13] = l(
																		`p`,
																		{
																			class: `text-xs text-gray-500 mt-1 font-medium`,
																		},
																		`Pending`,
																		-1
																	)),
															]
														),
														l(
															`button`,
															{
																id: `stride-card-postponed`,
																onClick: i[2] || (i[2] = (e) => Q(`postponed`)),
																class: `group bg-white rounded-2xl p-4 border border-gray-100 shadow-sm hover:shadow-md hover:border-red-200 transition-all duration-200 text-left`,
															},
															[
																i[14] ||
																	(i[14] = l(
																		`div`,
																		{
																			class: `w-9 h-9 rounded-xl bg-red-50 group-hover:bg-red-100 flex items-center justify-center mb-3 transition-colors`,
																		},
																		[
																			l(
																				`svg`,
																				{
																					class: `w-5 h-5 text-red-500`,
																					fill: `none`,
																					viewBox: `0 0 24 24`,
																					stroke: `currentColor`,
																					"stroke-width": `2`,
																				},
																				[
																					l(`path`, {
																						"stroke-linecap": `round`,
																						"stroke-linejoin": `round`,
																						d: `M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5`,
																					}),
																				]
																			),
																		],
																		-1
																	)),
																l(
																	`p`,
																	D,
																	c(q.value.payments.postponed.count),
																	1
																),
																i[15] ||
																	(i[15] = l(
																		`p`,
																		{
																			class: `text-xs text-gray-500 mt-1 font-medium`,
																		},
																		`Postponed`,
																		-1
																	)),
															]
														),
													]),
												]),
												q.value.vehicle
													? (t(),
													  a(`section`, O, [
															i[25] ||
																(i[25] = l(
																	`h2`,
																	{
																		class: `text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3 px-1`,
																	},
																	`Your Vehicle`,
																	-1
																)),
															l(`div`, k, [
																l(`div`, A, [
																	q.value.vehicle.vehicle_image
																		? (t(),
																		  a(
																				`img`,
																				{
																					key: 0,
																					src: q.value.vehicle.vehicle_image,
																					alt: Y.value,
																					class: `object-cover w-full h-full opacity-80`,
																				},
																				null,
																				8,
																				j
																		  ))
																		: (t(),
																		  a(`div`, M, [
																				...(i[17] ||
																					(i[17] = [
																						l(
																							`svg`,
																							{
																								class: `w-14 h-14 mx-auto mb-1 opacity-50`,
																								fill: `none`,
																								viewBox: `0 0 24 24`,
																								stroke: `currentColor`,
																							},
																							[
																								l(`path`, {
																									"stroke-linecap": `round`,
																									"stroke-linejoin": `round`,
																									"stroke-width": `1.2`,
																									d: `M9 17a2 2 0 11-4 0 2 2 0 014 0zm10 0a2 2 0 11-4 0 2 2 0 014 0zM3 11l1.26-5.26A2 2 0 016.22 4h11.56a2 2 0 011.96 1.74L21 11M3 11h18M3 11l-.5 3H21.5L21 11`,
																								}),
																							],
																							-1
																						),
																					])),
																		  ])),
																	l(
																		`span`,
																		{
																			class: d([
																				`absolute top-3 right-3 text-xs font-semibold px-2.5 py-1 rounded-full`,
																				ke.value,
																			]),
																		},
																		c(q.value.vehicle.vehicle_status || `—`),
																		3
																	),
																]),
																l(`div`, N, [
																	l(`div`, null, [
																		l(`p`, P, c(Y.value), 1),
																		l(
																			`p`,
																			F,
																			c(q.value.vehicle.license_plate),
																			1
																		),
																	]),
																	l(`div`, I, [
																		l(`div`, L, [
																			i[18] ||
																				(i[18] = l(
																					`p`,
																					{
																						class: `text-xs text-gray-400 uppercase tracking-wide font-medium`,
																					},
																					`Year`,
																					-1
																				)),
																			l(
																				`p`,
																				R,
																				c(
																					q.value.vehicle.year_of_manufacture ||
																						`—`
																				),
																				1
																			),
																		]),
																		l(`div`, z, [
																			i[19] ||
																				(i[19] = l(
																					`p`,
																					{
																						class: `text-xs text-gray-400 uppercase tracking-wide font-medium`,
																					},
																					`Color`,
																					-1
																				)),
																			l(
																				`p`,
																				B,
																				c(q.value.vehicle.color || `—`),
																				1
																			),
																		]),
																		l(`div`, V, [
																			i[20] ||
																				(i[20] = l(
																					`p`,
																					{
																						class: `text-xs text-gray-400 uppercase tracking-wide font-medium`,
																					},
																					`Fuel`,
																					-1
																				)),
																			l(
																				`p`,
																				H,
																				c(q.value.vehicle.fuel_type || `—`),
																				1
																			),
																		]),
																	]),
																	l(`div`, U, [
																		l(`div`, null, [
																			i[21] ||
																				(i[21] = l(
																					`p`,
																					{
																						class: `text-xs text-gray-400 font-medium`,
																					},
																					`Rate`,
																					-1
																				)),
																			l(
																				`p`,
																				le,
																				c(X(q.value.lease.rate)) +
																					` / ` +
																					c(q.value.lease.period_type),
																				1
																			),
																		]),
																		l(`div`, null, [
																			i[22] ||
																				(i[22] = l(
																					`p`,
																					{
																						class: `text-xs text-gray-400 font-medium`,
																					},
																					`Lease Period`,
																					-1
																				)),
																			l(
																				`p`,
																				W,
																				c(q.value.lease.start_date) +
																					` → ` +
																					c(q.value.lease.end_date),
																				1
																			),
																		]),
																		l(`div`, null, [
																			i[23] ||
																				(i[23] = l(
																					`p`,
																					{
																						class: `text-xs text-gray-400 font-medium`,
																					},
																					`Total Paid`,
																					-1
																				)),
																			l(
																				`p`,
																				ue,
																				c(X(q.value.lease.total_paid)),
																				1
																			),
																		]),
																		l(`div`, null, [
																			i[24] ||
																				(i[24] = l(
																					`p`,
																					{
																						class: `text-xs text-gray-400 font-medium`,
																					},
																					`Outstanding`,
																					-1
																				)),
																			l(
																				`p`,
																				de,
																				c(X(q.value.lease.total_outstanding)),
																				1
																			),
																		]),
																	]),
																]),
															]),
													  ]))
													: s(``, !0),
											],
											64
									  ))
									: s(``, !0),
							]),
							te(
								ee,
								{ name: `drawer` },
								{
									default: n(() => [
										Z.open
											? (t(),
											  a(`div`, fe, [
													l(`div`, {
														class: `absolute inset-0 bg-black/40 backdrop-blur-sm`,
														onClick: i[3] || (i[3] = (e) => (Z.open = !1)),
													}),
													l(`div`, pe, [
														l(`div`, me, [
															l(`div`, he, [
																l(
																	`div`,
																	{
																		class: d([
																			`w-8 h-8 rounded-xl flex items-center justify-center`,
																			Z.iconBg,
																		]),
																	},
																	[l(`span`, ge, c(Z.icon), 1)],
																	2
																),
																l(`div`, null, [
																	l(`h3`, _e, c(Z.title), 1),
																	l(
																		`p`,
																		ve,
																		c(Z.rows.length) +
																			` period` +
																			c(Z.rows.length === 1 ? `` : `s`),
																		1
																	),
																]),
															]),
															l(
																`button`,
																{
																	onClick:
																		i[4] || (i[4] = (e) => (Z.open = !1)),
																	class: `w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-400 hover:bg-gray-200 transition-colors`,
																},
																[
																	...(i[26] ||
																		(i[26] = [
																			l(
																				`svg`,
																				{
																					class: `w-4 h-4`,
																					fill: `none`,
																					viewBox: `0 0 24 24`,
																					stroke: `currentColor`,
																					"stroke-width": `2.5`,
																				},
																				[
																					l(`path`, {
																						"stroke-linecap": `round`,
																						"stroke-linejoin": `round`,
																						d: `M6 18L18 6M6 6l12 12`,
																					}),
																				],
																				-1
																			),
																		])),
																]
															),
														]),
														l(`div`, ye, [
															(t(!0),
															a(
																h,
																null,
																r(
																	Z.rows,
																	(e) => (
																		t(),
																		a(
																			`div`,
																			{
																				key: e.name,
																				class: `bg-gray-50 rounded-xl p-3.5 border border-gray-100`,
																			},
																			[
																				l(`div`, be, [
																					l(`div`, null, [
																						l(
																							`span`,
																							xe,
																							`Period ` + c(e.period),
																							1
																						),
																						l(`p`, Se, [
																							Z.type === `paid`
																								? (t(),
																								  a(
																										h,
																										{ key: 0 },
																										[
																											o(
																												c(e.from_date) +
																													` → ` +
																													c(e.to_date),
																												1
																											),
																										],
																										64
																								  ))
																								: (t(),
																								  a(
																										h,
																										{ key: 1 },
																										[o(c(e.due_date), 1)],
																										64
																								  )),
																						]),
																					]),
																					l(`span`, Ce, c(X(e.amount)), 1),
																				]),
																				Z.type === `paid` && e.payment_entry
																					? (t(),
																					  a(`div`, we, [
																							i[27] ||
																								(i[27] = l(
																									`svg`,
																									{
																										class: `w-3 h-3 text-emerald-500 flex-shrink-0`,
																										fill: `none`,
																										viewBox: `0 0 24 24`,
																										stroke: `currentColor`,
																										"stroke-width": `2`,
																									},
																									[
																										l(`path`, {
																											"stroke-linecap": `round`,
																											"stroke-linejoin": `round`,
																											d: `M9 12l2 2 4-4`,
																										}),
																									],
																									-1
																								)),
																							l(
																								`span`,
																								Te,
																								c(e.payment_entry),
																								1
																							),
																					  ]))
																					: s(``, !0),
																				Z.type === `invoiced` && e.sales_invoice
																					? (t(),
																					  a(`div`, Ee, [
																							i[28] ||
																								(i[28] = l(
																									`svg`,
																									{
																										class: `w-3 h-3 text-amber-500 flex-shrink-0`,
																										fill: `none`,
																										viewBox: `0 0 24 24`,
																										stroke: `currentColor`,
																										"stroke-width": `2`,
																									},
																									[
																										l(`path`, {
																											"stroke-linecap": `round`,
																											"stroke-linejoin": `round`,
																											d: `M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2`,
																										}),
																									],
																									-1
																								)),
																							l(
																								`span`,
																								De,
																								`Invoice: ` +
																									c(e.sales_invoice),
																								1
																							),
																					  ]))
																					: s(``, !0),
																			]
																		)
																	)
																),
																128
															)),
															Z.rows.length === 0
																? (t(),
																  a(`div`, Oe, [
																		...(i[29] ||
																			(i[29] = [
																				l(
																					`p`,
																					{ class: `text-sm` },
																					`No records found.`,
																					-1
																				),
																			])),
																  ]))
																: s(``, !0),
														]),
													]),
											  ]))
											: s(``, !0),
									]),
									_: 1,
								}
							),
						])
					);
				};
			},
		},
		[[`__scopeId`, `data-v-22bccf86`]]
	);
export { G as default };
//# sourceMappingURL=Home-_sYUadsn.js.map
