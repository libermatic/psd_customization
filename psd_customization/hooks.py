# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__

app_name = "psd_customization"
app_version = __version__
app_title = "PSD SELF Customization"
app_publisher = "Libermatic"
app_description = "Customizations for PSD SELF"
app_icon = "fa fa-cubes"
app_color = "#9C27B0"
app_email = "info@libermatic.com"
app_license = "MIT"

error_report_email = "support@libermatic.com"

fixtures = [
    {
        "doctype": "Property Setter",
        "filters": [
            [
                "name",
                "in",
                [
                    "Batch-batch_id-reqd",
                    "Batch-batch_id-default",
                    "Batch-expiry_date-bold",
                    "Purchase Invoice Item-qty-columns",
                    "Purchase Invoice Item-rate-columns",
                    "Purchase Invoice Item-batch_no-in_list_view",
                    "Purchase Invoice Item-batch_no-columns",
                    "Sales Invoice-subscription_section-collapsible",
                    "Sales Invoice Item-item_code-columns",
                    "Sales Invoice Item-warehouse-in_list_view",
                    "Purchase Invoice-is_paid-default",
                    "Purchase Invoice-update_stock-default",
                    "Salary Slip-end_date-read_only",
                ],
            ]
        ],
    },
    {
        "doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                [
                    "Branch-company",
                    "Journal Entry-branch",
                    "Sales Invoice-gym_member",
                    "Sales Invoice-gym_member_name",
                    "Sales Invoice-gym_subscription_details_section",
                    "Sales Invoice-gym_subscription_details_html",
                    "Sales Invoice Item-gym_section",
                    "Sales Invoice Item-is_gym_subscription",
                    "Sales Invoice Item-gym_subscription",
                    "Sales Invoice Item-gym_is_lifetime",
                    "Sales Invoice Item-gym_trainer",
                    "Sales Invoice Item-gym_training_slot",
                    "Sales Invoice Item-gym_col0",
                    "Sales Invoice Item-gym_from_date",
                    "Sales Invoice Item-gym_to_date",
                    "Purchase Receipt Item-parse_serial",
                    "Purchase Invoice Item-parse_serial",
                    "Salary Structure-training_earning_detail",
                    "Salary Structure-salary_slip_based_on_training",
                    "Salary Structure-training_earning_detail_cb",
                    "Salary Structure-training_salary_component",
                    "Salary Structure-training_monthly_rate",
                    "Salary Slip-salary_slip_based_on_training",
                    "Salary Slip-training_section",
                    "Salary Slip-trainings",
                    "Salary Slip-training_cb",
                    "Salary Slip-actual_training_months",
                    "Salary Slip-total_training_months",
                    "Salary Slip-training_rate",
                ],
            ]
        ],
    },
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = ["/assets/css/psd_customization.css"]
app_include_js = [
    "/assets/js/psd_customization.min.js",
    "/assets/psd_customization/js/naming_series.js",
    "/assets/psd_customization/js/gym_member_quick_entry.js",
    "/assets/psd_customization/js/psd_customization.iife.js",
]

# include js, css files in header of web template
# web_include_css = "/assets/psd_customization/css/psd_customization.css"
# web_include_js = "/assets/psd_customization/js/psd_customization.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Journal Entry": "public/js/journal_entry.js",
    "Item": "public/js/item.js",
    "Purchase Receipt": "public/js/serial_reader.js",
    "Purchase Invoice": "public/js/serial_reader.js",
    "Sales Invoice": "public/js/cscripts/sales_invoice.js",
    "Salary Structure": "public/js/cscripts/salary_structure.js",
    "Salary Slip": "public/js/cscripts/salary_slip.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "psd_customization.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "psd_customization.install.before_install"
# after_install = "psd_customization.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = \
# 	"psd_customization.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Batch": {
        "before_save": "psd_customization.doc_events.batch.before_save",
        "autoname": "psd_customization.doc_events.batch.autoname",
    },
    "Sales Invoice": {
        "validate": "psd_customization.doc_events.sales_invoice.validate",
        "on_submit": "psd_customization.doc_events.sales_invoice.on_submit",
        "on_cancel": "psd_customization.doc_events.sales_invoice.on_cancel",
    },
    "Salary Slip": {
        "before_insert": "psd_customization.doc_events.salary_slip.before_insert",
        "on_submit": "psd_customization.doc_events.salary_slip.on_submit",
        "on_cancel": "psd_customization.doc_events.salary_slip.on_cancel",
    },
}

on_session_creation = "psd_customization.doc_events.defaults.set_user_defaults"

# Scheduled Tasks
# ---------------

scheduler_events = {"daily": ["psd_customization.tasks.daily"]}

# 	"all": ["psd_customization.tasks.all"],
# 	"hourly": ["psd_customization.tasks.hourly"],
# 	"weekly": ["psd_customization.tasks.weekly"]
# 	"monthly": ["psd_customization.tasks.monthly"]

# Testing
# -------

# before_tests = "psd_customization.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events":
# 	 "psd_customization.event.get_events"
# }
