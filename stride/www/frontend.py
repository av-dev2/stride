import json

import frappe
from frappe.utils import get_system_timezone

no_cache = 1


def get_context():
	csrf_token = frappe.sessions.get_csrf_token()
	context = frappe._dict()
	boot = get_boot()
	boot.csrf_token = csrf_token
	context.boot = frappe.as_json(boot)
	return context


@frappe.whitelist(methods=["POST"])
def get_context_for_dev():
	if not frappe.conf.developer_mode:
		frappe.throw(frappe._("This method is only meant for developer mode"))
	return json.loads(frappe.as_json(get_boot()))


def get_boot():
	return frappe._dict(
		{
			"frappe_version": frappe.__version__,
			"site_name": frappe.local.site,
			"read_only_mode": frappe.flags.read_only,
			"system_timezone": get_system_timezone(),
			"csrf_token": frappe.sessions.get_csrf_token(),
		}
	)
