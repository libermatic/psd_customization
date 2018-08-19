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

fixtures = [
    {
        'doctype': 'Property Setter',
        'filters': [['name', 'in', [
            'Batch-batch_id-reqd',
            'Batch-batch_id-default',
            'Batch-expiry_date-bold',
            'Purchase Invoice Item-qty-columns',
            'Purchase Invoice Item-rate-columns',
            'Purchase Invoice Item-batch_no-in_list_view',
            'Purchase Invoice Item-batch_no-columns',
            'Sales Invoice-update_stock-default',
            'Purchase Invoice-is_paid-default',
            'Purchase Invoice-update_stock-default',
        ]]],
    },
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/psd_customization/css/psd_customization.css"
app_include_js = [
    '/assets/psd_customization/js/naming_series.js',
    '/assets/psd_customization/js/gym_member_quick_entry.js',
]

# include js, css files in header of web template
# web_include_css = "/assets/psd_customization/css/psd_customization.css"
# web_include_js = "/assets/psd_customization/js/psd_customization.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#   "Role": "home_page"
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
#   "psd_customization.notifications.get_notification_config"

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
    'Batch': {
        'before_save': 'psd_customization.doc_events.batch.before_save',
        'autoname': 'psd_customization.doc_events.batch.autoname',
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"psd_customization.tasks.all"
# 	],
# 	"daily": [
# 		"psd_customization.tasks.daily"
# 	],
# 	"hourly": [
# 		"psd_customization.tasks.hourly"
# 	],
# 	"weekly": [
# 		"psd_customization.tasks.weekly"
# 	]
# 	"monthly": [
# 		"psd_customization.tasks.monthly"
# 	]
# }

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
