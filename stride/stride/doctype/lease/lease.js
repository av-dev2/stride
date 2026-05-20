// Copyright (c) 2024, elius-dev and contributors
// For license information, please see license.txt

frappe.ui.form.on("Lease", {
	setup(frm) {
		// Only show submitted Rental Contracts
		frm.set_query("rental_contract", () => ({
			filters: { docstatus: 1 },
		}));
	},

	refresh(frm) {
		frm.trigger("set_status_indicator");
		if (frm.doc.docstatus === 1 && frm.doc.payment_schedule?.length) {
			stride_render_lease_dashboard(frm);
		}
	},

	set_status_indicator(frm) {
		if (frm.doc.docstatus === 0) return;

		const colors = {
			Active: "blue",
			Completed: "green",
			Overdue: "red",
			Cancelled: "grey",
		};

		const color = colors[frm.doc.status] || "grey";
		frm.page.set_indicator(frm.doc.status, color);
	},
});

function stride_render_lease_dashboard(frm) {
	// Count schedule rows by status
	const counts = { Pending: 0, Invoiced: 0, Paid: 0, Overdue: 0 };
	const amounts = { Pending: 0, Invoiced: 0, Paid: 0, Overdue: 0 };

	(frm.doc.payment_schedule || []).forEach((row) => {
		const s = row.status || "Pending";
		counts[s] = (counts[s] || 0) + 1;
		amounts[s] = (amounts[s] || 0) + (row.amount || 0);
	});

	const total = frm.doc.payment_schedule.length;
	const total_amount = frm.doc.total_amount || 0;

	// Status config
	const config = {
		Paid: { color: "#2ecc71", label: "Paid" },
		Invoiced: { color: "#3498db", label: "Invoiced" },
		Pending: { color: "#f39c12", label: "Pending" },
		Overdue: { color: "#e74c3c", label: "Overdue" },
	};

	// Build segmented progress bar
	let bar_segments = "";
	for (const [status, cfg] of Object.entries(config)) {
		const pct = total > 0 ? (counts[status] / total) * 100 : 0;
		if (pct > 0) {
			bar_segments += `
				<div style="
					width: ${pct}%;
					background: ${cfg.color};
					height: 100%;
					transition: width 0.3s ease;
				" title="${cfg.label}: ${counts[status]} of ${total} (${pct.toFixed(
				0
			)}%)"></div>
			`;
		}
	}

	// Build KPI cards
	let kpi_cards = "";
	for (const [status, cfg] of Object.entries(config)) {
		kpi_cards += `
			<div style="
				flex: 1;
				min-width: 100px;
				padding: 10px 14px;
				border-radius: 8px;
				background: var(--card-bg);
				border-left: 3px solid ${cfg.color};
				text-align: center;
			">
				<div style="
					font-size: 11px;
					font-weight: 600;
					text-transform: uppercase;
					letter-spacing: 0.5px;
					color: ${cfg.color};
					margin-bottom: 4px;
				">${cfg.label}</div>
				<div style="
					font-size: 20px;
					font-weight: 700;
					color: var(--text-color);
				">${counts[status]}</div>
				<div style="
					font-size: 12px;
					color: var(--text-muted);
					margin-top: 2px;
				">${format_currency(amounts[status])}</div>
			</div>
		`;
	}

	// Paid percentage for display
	const paid_pct =
		total_amount > 0 ? ((frm.doc.total_paid || 0) / total_amount) * 100 : 0;

	const html = `
		<div class="stride-lease-dashboard" style="margin-bottom: 16px;">
			<div style="
				font-size: 12px;
				font-weight: 600;
				text-transform: uppercase;
				letter-spacing: 0.8px;
				color: var(--text-muted);
				margin-bottom: 10px;
			">
				Payment Progress
			</div>

			<!-- Progress Bar -->
			<div style="
				width: 100%;
				height: 10px;
				background: var(--border-color);
				border-radius: 5px;
				overflow: hidden;
				display: flex;
				margin-bottom: 14px;
			">
				${bar_segments}
			</div>

			<!-- KPI Cards -->
			<div style="
				display: flex;
				gap: 10px;
				flex-wrap: wrap;
				margin-bottom: 10px;
			">
				${kpi_cards}
			</div>

			<!-- Summary Footer -->
			<div style="
				padding: 8px 12px;
				background: var(--subtle-fg);
				border-radius: 6px;
				display: flex;
				justify-content: space-between;
				flex-wrap: wrap;
				gap: 8px;
				font-size: 13px;
			">
				<span style="color: var(--text-muted);">
					Collected: <strong style="color: #2ecc71;">${format_currency(
						frm.doc.total_paid || 0
					)}</strong>
					of ${format_currency(total_amount)}
					(${paid_pct.toFixed(1)}%)
				</span>
				<span style="color: var(--text-muted);">
					Outstanding: <strong style="color: ${
						(frm.doc.total_outstanding || 0) > 0
							? "#e74c3c"
							: "var(--text-color)"
					};">
						${format_currency(frm.doc.total_outstanding || 0)}
					</strong>
				</span>
			</div>
		</div>
	`;

	// Remove previous dashboard to avoid duplicates
	if (frm.dashboard.wrapper) {
		frm.dashboard.wrapper.find(".stride-lease-dashboard").remove();
		frm.dashboard.wrapper.append(html);
	}
}
