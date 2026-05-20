// Vehicle client script for Stride — Payment KPI Dashboard
// Loaded via doctype_js hook

frappe.ui.form.on("Vehicle", {
	setup(frm) {
		// Rental Service: non-stock service item used for Sales Invoice lines
		frm.set_query("rental_service", () => ({
			filters: { disabled: 0, is_stock_item: 0 },
		}));

		// Rental Item (Asset): stock item used in Material Issue when ownership is transferred
		frm.set_query("rental_item", () => ({
			filters: { disabled: 0, is_stock_item: 1 },
		}));
	},

	refresh(frm) {
		if (!frm.is_new()) {
			stride_render_payment_kpis(frm);
		}
	},
});

function stride_render_payment_kpis(frm) {
	frappe.call({
		method: "stride.api.vehicle.get_vehicle_payment_kpis",
		args: { vehicle: frm.doc.name },
		callback(r) {
			if (!r.message || !r.message.total_periods) {
				return;
			}

			const data = r.message;
			const statuses = data.statuses || {};

			// Status config: label, color, icon
			const status_config = {
				Pending: { color: "#f39c12", icon: "clock" },
				Invoiced: { color: "#3498db", icon: "file" },
				Paid: { color: "#2ecc71", icon: "check" },
				Overdue: { color: "#e74c3c", icon: "alert-circle" },
			};

			let cards_html = "";
			for (const [status, config] of Object.entries(status_config)) {
				const info = statuses[status] || { count: 0, amount: 0 };
				cards_html += `
					<div class="stride-kpi-card" style="
						flex: 1;
						min-width: 120px;
						padding: 12px 16px;
						border-radius: 8px;
						background: var(--card-bg);
						border: 1px solid var(--border-color);
						text-align: center;
					">
						<div style="
							font-size: 11px;
							font-weight: 600;
							text-transform: uppercase;
							letter-spacing: 0.5px;
							color: ${config.color};
							margin-bottom: 6px;
						">
							${status}
						</div>
						<div style="
							font-size: 22px;
							font-weight: 700;
							color: var(--text-color);
							line-height: 1.2;
						">
							${info.count}
						</div>
						<div style="
							font-size: 12px;
							color: var(--text-muted);
							margin-top: 4px;
						">
							${format_currency(info.amount)}
						</div>
					</div>
				`;
			}

			const section_html = `
				<div class="stride-payment-kpis" style="margin-bottom: 16px;">
					<div style="
						font-size: 12px;
						font-weight: 600;
						text-transform: uppercase;
						letter-spacing: 0.8px;
						color: var(--text-muted);
						margin-bottom: 10px;
						padding-left: 2px;
					">
						Lease Payment Summary
					</div>
					<div style="
						display: flex;
						gap: 12px;
						flex-wrap: wrap;
					">
						${cards_html}
					</div>
					<div style="
						margin-top: 10px;
						padding: 8px 12px;
						background: var(--subtle-fg);
						border-radius: 6px;
						display: flex;
						justify-content: space-between;
						font-size: 13px;
					">
						<span style="color: var(--text-muted);">
							Total Periods: <strong style="color: var(--text-color);">${
								data.total_periods
							}</strong>
						</span>
						<span style="color: var(--text-muted);">
							Total Amount: <strong style="color: var(--text-color);">${format_currency(
								data.total_amount
							)}</strong>
						</span>
					</div>
				</div>
			`;

			// Remove previous KPI section if exists (avoid duplicates on refresh)
			$(frm.fields_dict.license_plate.wrapper)
				.closest(".frappe-control")
				.siblings(".stride-payment-kpis")
				.remove();

			// Insert after the form dashboard section
			if (frm.dashboard.wrapper) {
				frm.dashboard.wrapper.find(".stride-payment-kpis").remove();
				frm.dashboard.wrapper.append(section_html);
			}
		},
	});
}
