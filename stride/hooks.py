app_name = "stride"
app_title = "Stride"
app_publisher = "elius-dev"
app_description = "Vehicle rental management app"
app_email = "[EMAIL_ADDRESS]"
app_license = "mit"

# Apps
# ------------------

required_apps = ["frappe", "erpnext"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "stride",
# 		"logo": "/assets/stride/logo.png",
# 		"title": "Stride",
# 		"route": "/stride",
# 		"has_permission": "stride.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/stride/css/stride.css"
# app_include_js = "/assets/stride/js/stride.js"

# include js, css files in header of web template
# web_include_css = "/assets/stride/css/stride.css"
# web_include_js = "/assets/stride/js/stride.js"

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}

# doctype_list_js = {
# 	"Custom Field": "stride/patches/custom_fields/custom_field.js",
# 	"Property Setter": "stride/patches/property_setter/property_setter.js",
# }


# Installation
# ------------

# after_install = "stride.setup.after_install"

# Migrate
# -------
# Custom fields and property setters (hms_tz pattern) — Task 3

# after_migrate = [
# 	"stride.patches.custom_fields.create_custom_fields.execute",
# 	"stride.patches.property_setter.create_property_setters.execute",
# ]


# Document Events
# ---------------

# doc_events = {
# 	"Payment Entry": {
# 		"on_submit": "stride.overrides.payment_entry.on_submit",
# 		"on_cancel": "stride.overrides.payment_entry.on_cancel",
# 	},
# 	"Payment Reconciliation": {
# 		"on_submit": "stride.overrides.payment_reconciliation.on_submit",
# 	},
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"daily": ["stride.tasks.generate_lease_invoices"],
# 	"cron": {
# 		"*/15 * * * *": ["stride.tasks.poll_gps_data"],
# 	},
# }

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True
