import {
	F as e,
	G as t,
	J as n,
	K as r,
	N as i,
	R as a,
	S as o,
	dt as s,
	h as c,
	k as l,
	p as u,
	rt as d,
	t as f,
	tt as p,
} from "./asyncToGenerator-COJlnFvb.js";
import {
	C as m,
	D as h,
	S as g,
	T as _,
	_ as v,
	b as y,
	h as b,
	u as x,
	v as S,
	w as C,
	y as w,
} from "./TooltipBubble-BfBzZZ5Q.js";
function T() {
	let e = document.activeElement;
	if (e == null) return null;
	for (
		;
		e != null && e.shadowRoot != null && e.shadowRoot.activeElement != null;

	)
		e = e.shadowRoot.activeElement;
	return e;
}
var E = m(() => {
	let e = d(new Map()),
		n = d(),
		r = u(() => {
			for (let t of e.value.values()) if (t) return !0;
			return !1;
		}),
		i = S({ scrollBody: d(!0) }),
		a = null,
		o = () => {
			var e;
			(document.body.style.paddingRight = ``),
				(document.body.style.marginRight = ``),
				(document.body.style.pointerEvents = ``),
				document.documentElement.style.removeProperty(`--scrollbar-width`),
				(document.body.style.overflow = (e = n.value) == null ? `` : e),
				_ && (a == null || a()),
				(n.value = void 0);
		};
	return (
		t(
			r,
			(e, t) => {
				var s;
				if (!C) return;
				if (!e) {
					t && o();
					return;
				}
				n.value === void 0 && (n.value = document.body.style.overflow);
				let c = window.innerWidth - document.documentElement.clientWidth,
					u = { padding: c, margin: 0 },
					d =
						(s = i.scrollBody) != null && s.value
							? typeof i.scrollBody.value == `object`
								? v(
										{
											padding:
												i.scrollBody.value.padding === !0
													? c
													: i.scrollBody.value.padding,
											margin:
												i.scrollBody.value.margin === !0
													? c
													: i.scrollBody.value.margin,
										},
										u
								  )
								: u
							: { padding: 0, margin: 0 };
				c > 0 &&
					((document.body.style.paddingRight =
						typeof d.padding == `number`
							? `${d.padding}px`
							: String(d.padding)),
					(document.body.style.marginRight =
						typeof d.margin == `number` ? `${d.margin}px` : String(d.margin)),
					document.documentElement.style.setProperty(
						`--scrollbar-width`,
						`${c}px`
					),
					(document.body.style.overflow = `hidden`)),
					_ && (a = y(document, `touchmove`, (e) => k(e), { passive: !1 })),
					l(() => {
						r.value &&
							((document.body.style.pointerEvents = `none`),
							(document.body.style.overflow = `hidden`));
					});
			},
			{ immediate: !0, flush: `sync` }
		),
		e
	);
});
function D(e) {
	let t = Math.random().toString(36).substring(2, 7),
		n = E();
	n.value.set(t, e == null ? !1 : e);
	let r = u({
		get: () => {
			var e;
			return (e = n.value.get(t)) == null ? !1 : e;
		},
		set: (e) => n.value.set(t, e),
	});
	return (
		h(() => {
			n.value.delete(t);
		}),
		r
	);
}
function O(e) {
	let t = window.getComputedStyle(e);
	if (
		t.overflowX === `scroll` ||
		t.overflowY === `scroll` ||
		(t.overflowX === `auto` && e.clientWidth < e.scrollWidth) ||
		(t.overflowY === `auto` && e.clientHeight < e.scrollHeight)
	)
		return !0;
	{
		let t = e.parentNode;
		return !(t instanceof Element) || t.tagName === `BODY` ? !1 : O(t);
	}
}
function k(e) {
	let t = e || window.event,
		n = t.target;
	return n instanceof Element && O(n)
		? !1
		: t.touches.length > 1
		? !0
		: (t.preventDefault && t.cancelable && t.preventDefault(), !1);
}
var A = function (e) {
		return typeof document > `u`
			? null
			: (Array.isArray(e) ? e[0] : e).ownerDocument.body;
	},
	j = new WeakMap(),
	M = new WeakMap(),
	N = {},
	P = 0,
	F = function (e) {
		return e && (e.host || F(e.parentNode));
	},
	I = function (e, t) {
		return t
			.map(function (t) {
				if (e.contains(t)) return t;
				var n = F(t);
				return n && e.contains(n)
					? n
					: (console.error(
							`aria-hidden`,
							t,
							`in not contained inside`,
							e,
							`. Doing nothing`
					  ),
					  null);
			})
			.filter(function (e) {
				return !!e;
			});
	},
	L = function (e, t, n, r) {
		var i = I(t, Array.isArray(e) ? e : [e]);
		N[n] || (N[n] = new WeakMap());
		var a = N[n],
			o = [],
			s = new Set(),
			c = new Set(i),
			l = function (e) {
				!e || s.has(e) || (s.add(e), l(e.parentNode));
			};
		i.forEach(l);
		var u = function (e) {
			!e ||
				c.has(e) ||
				Array.prototype.forEach.call(e.children, function (e) {
					if (s.has(e)) u(e);
					else
						try {
							var t = e.getAttribute(r),
								i = t !== null && t !== `false`,
								c = (j.get(e) || 0) + 1,
								l = (a.get(e) || 0) + 1;
							j.set(e, c),
								a.set(e, l),
								o.push(e),
								c === 1 && i && M.set(e, !0),
								l === 1 && e.setAttribute(n, `true`),
								i || e.setAttribute(r, `true`);
						} catch (t) {
							console.error(`aria-hidden: cannot operate on `, e, t);
						}
				});
		};
		return (
			u(t),
			s.clear(),
			P++,
			function () {
				o.forEach(function (e) {
					var t = j.get(e) - 1,
						i = a.get(e) - 1;
					j.set(e, t),
						a.set(e, i),
						t || (M.has(e) || e.removeAttribute(r), M.delete(e)),
						i || e.removeAttribute(n);
				}),
					P--,
					P ||
						((j = new WeakMap()),
						(j = new WeakMap()),
						(M = new WeakMap()),
						(N = {}));
			}
		);
	},
	R = function (e, t, n) {
		n === void 0 && (n = `data-aria-hidden`);
		var r = Array.from(Array.isArray(e) ? e : [e]),
			i = t || A(e);
		return i
			? (r.push.apply(r, Array.from(i.querySelectorAll(`[aria-live], script`))),
			  L(r, i, n, `aria-hidden`))
			: function () {
					return null;
			  };
	};
function z(e) {
	let n;
	t(
		() => w(e),
		(e) => {
			let t = !1;
			try {
				t = !!(e != null && e.closest(`[popover]:not(:popover-open)`));
			} catch (e) {}
			e && !t ? (n = R(e)) : n && n();
		}
	),
		i(() => {
			n && n();
		});
}
var B = g(() => d([]));
function V() {
	let e = B();
	return {
		add(t) {
			let n = e.value[0];
			t !== n && (n == null || n.pause()),
				(e.value = H(e.value, t)),
				e.value.unshift(t);
		},
		remove(t) {
			var n;
			(e.value = H(e.value, t)), (n = e.value[0]) == null || n.resume();
		},
	};
}
function H(e, t) {
	let n = [...e],
		r = n.indexOf(t);
	return r !== -1 && n.splice(r, 1), n;
}
var U = `focusScope.autoFocusOnMount`,
	W = `focusScope.autoFocusOnUnmount`,
	G = { bubbles: !1, cancelable: !0 };
function K(e, { select: t = !1 } = {}) {
	let n = T();
	for (let r of e) if ((Q(r, { select: t }), T() !== n)) return !0;
}
function q(e) {
	let t = J(e);
	return [Y(t, e), Y(t.reverse(), e)];
}
function J(e) {
	let t = [],
		n = document.createTreeWalker(e, NodeFilter.SHOW_ELEMENT, {
			acceptNode: (e) => {
				let t = e.tagName === `INPUT` && e.type === `hidden`;
				return e.disabled || e.hidden || t
					? NodeFilter.FILTER_SKIP
					: e.tabIndex >= 0
					? NodeFilter.FILTER_ACCEPT
					: NodeFilter.FILTER_SKIP;
			},
		});
	for (; n.nextNode(); ) t.push(n.currentNode);
	return t;
}
function Y(e, t) {
	for (let n of e) if (!X(n, { upTo: t })) return n;
}
function X(e, { upTo: t }) {
	if (getComputedStyle(e).visibility === `hidden`) return !0;
	for (; e; ) {
		if (t !== void 0 && e === t) return !1;
		if (getComputedStyle(e).display === `none`) return !0;
		e = e.parentElement;
	}
	return !1;
}
function Z(e) {
	return e instanceof HTMLInputElement && `select` in e;
}
function Q(e, { select: t = !1 } = {}) {
	if (e && e.focus) {
		let n = T();
		e.focus({ preventScroll: !0 }), e !== n && Z(e) && t && e.select();
	}
}
var $ = o({
	__name: `FocusScope`,
	props: {
		loop: { type: Boolean, required: !1, default: !1 },
		trapped: { type: Boolean, required: !1, default: !1 },
		asChild: { type: Boolean, required: !1 },
		as: { type: null, required: !1 },
	},
	emits: [`mountAutoFocus`, `unmountAutoFocus`],
	setup(t, { emit: i }) {
		let o = t,
			u = i,
			{ currentRef: m, currentElement: h } = b(),
			g = d(null),
			_ = V(),
			v = p({
				paused: !1,
				pause() {
					this.paused = !0;
				},
				resume() {
					this.paused = !1;
				},
			});
		r((e) => {
			if (!C) return;
			let t = h.value;
			if (!o.trapped) return;
			function n(e) {
				if (v.paused || !t) return;
				let n = e.target;
				t.contains(n) ? (g.value = n) : Q(g.value, { select: !0 });
			}
			function r(e) {
				if (v.paused || !t) return;
				let n = e.relatedTarget;
				n !== null && (t.contains(n) || Q(g.value, { select: !0 }));
			}
			function i(e) {
				let n = g.value;
				n !== null &&
					e.some((e) => e.removedNodes.length > 0) &&
					(t.contains(n) || Q(t));
			}
			document.addEventListener(`focusin`, n),
				document.addEventListener(`focusout`, r);
			let a = new MutationObserver(i);
			t && a.observe(t, { childList: !0, subtree: !0 }),
				e(() => {
					document.removeEventListener(`focusin`, n),
						document.removeEventListener(`focusout`, r),
						a.disconnect();
				});
		}),
			r(
				(function () {
					var e = f(function* (e) {
						let t = h.value;
						if ((yield l(), !t)) return;
						_.add(v);
						let n = T();
						if (!t.contains(n)) {
							let e = new CustomEvent(U, G);
							t.addEventListener(U, (e) => u(`mountAutoFocus`, e)),
								t.dispatchEvent(e),
								e.defaultPrevented ||
									(K(J(t), { select: !0 }), T() === n && Q(t));
						}
						e(() => {
							t.removeEventListener(U, (e) => u(`mountAutoFocus`, e));
							let e = new CustomEvent(W, G),
								r = (e) => {
									u(`unmountAutoFocus`, e);
								};
							t.addEventListener(W, r),
								t.dispatchEvent(e),
								setTimeout(() => {
									e.defaultPrevented ||
										Q(n == null ? document.body : n, { select: !0 }),
										t.removeEventListener(W, r),
										_.remove(v);
								}, 0);
						});
					});
					return function (t) {
						return e.apply(this, arguments);
					};
				})()
			);
		function y(e) {
			if ((!o.loop && !o.trapped) || v.paused) return;
			let t = e.key === `Tab` && !e.altKey && !e.ctrlKey && !e.metaKey,
				n = T();
			if (t && n) {
				let t = e.currentTarget,
					[r, i] = q(t);
				r && i
					? !e.shiftKey && n === i
						? (e.preventDefault(), o.loop && Q(r, { select: !0 }))
						: e.shiftKey &&
						  n === r &&
						  (e.preventDefault(), o.loop && Q(i, { select: !0 }))
					: n === t && e.preventDefault();
			}
		}
		return (t, r) => (
			e(),
			c(
				s(x),
				{
					ref_key: `currentRef`,
					ref: m,
					tabindex: `-1`,
					"as-child": t.asChild,
					as: t.as,
					onKeydown: y,
				},
				{ default: n(() => [a(t.$slots, `default`)]), _: 3 },
				8,
				[`as-child`, `as`]
			)
		);
	},
});
export { T as i, z as n, D as r, $ as t };
//# sourceMappingURL=FocusScope-IRrUVxOh.js.map
