# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "selco"
app_title = "Selco"
app_publisher = "Selco"
app_description = "Selco"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "basawaraj@selco-india.com"
app_version = "0.0.1"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/selco/css/selco.css"
# app_include_js = "/assets/selco/js/selco.js"
#app_include_js = "/assets/js/selco.min.js"

# include js, css files in header of web template
# web_include_css = "/assets/selco/css/selco.css"
# web_include_js = "/assets/selco/js/selco.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#    "Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "selco.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "selco.install.before_install"
# after_install = "selco.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "selco.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#     "Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#     "Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events
doc_events = {

    "Issue": {
         "validate": "selco.selco_customizations.selco_issue_updates"
    },
    "Warranty Claim": {
         "validate": "selco.selco_customizations.selco_warranty_claim_updates"
    },
    "Delivery Note": {
         "before_insert": "selco.selco_customizations.selco_delivery_note_before_insert",
         "on_submit": "selco.selco_customizations.selco_delivery_note_updates"
    },
    "Material Request": {
         "validate": "selco.selco_customizations.selco_material_request_updates",
         "before_insert": "selco.selco_customizations.selco_material_request_before_insert"
         #"on_update":"selco.selco_customizations.selco_material_approved_and_dispatched"
    },
    "Purchase Receipt": {
         "before_insert": "selco.selco_customizations.selco_purchase_receipt_before_insert",
         "validate": "selco.selco_customizations.selco_purchase_receipt_updates",
    },
    "Stock Entry": {
         "before_insert": "selco.selco_customizations.selco_stock_entry_updates",
         "validate": "selco.selco_customizations.selco_stock_entry_validate",         
         "before_save": "selco.selco_customizations.selco_stock_entry_updates",
         "on_submit": "selco.selco_customizations.selco_stock_entry_on_submit_updates",
         "on_cancel": "selco.selco_customizations.selco_stock_entry_on_cancel_updates"
    },
    "Customer": {
         "before_insert": "selco.selco_customizations.selco_customer_before_insert",
         "validate": "selco.selco_customizations.selco_customer_updates"
    },
    "Sales Invoice": {
         "before_insert": "selco.selco_customizations.selco_sales_invoice_before_insert",
         "validate": "selco.selco_customizations.selco_sales_invoice_validate"
    },
    "Payment Entry": {
         "before_insert": "selco.selco_customizations.selco_payment_entry_before_insert",
         "validate": "selco.selco_customizations.selco_payment_entry_update"
    },
    "Journal Entry": {
         "before_insert": "selco.selco_customizations.selco_journal_entry_before_insert"
         #"on_submit": "selco.selco_customizations.selco_journal_entry_on_submit"
    },
    "Purchase Invoice": {
         "before_insert": "selco.selco_customizations.selco_purchase_invoice_before_insert",
         "validate": "selco.selco_customizations.selco_purchase_invoice_validate"
    },
    "Warehouse Type": {
         "validate": "selco.selco_customizations.clean_up"
    },
    "Lead": {
         "before_insert": "selco.selco_customizations.selco_lead_before_insert",
         "validate": "selco.selco_customizations.selco_lead_validate"
    },
    "Address": {
         "before_insert": "selco.selco_customizations.selco_address_before_insert"
    },
    "Service Call": {
        "before_insert": "selco.selco_customizations.month_service_person_unique"
    }
 }

# scheduler_events = {
#     "all": [
#         "selco.tasks.all"
#     ],
#     "daily": [
#         "selco.tasks.daily"
#     ],
#     "hourly": [
#         "selco.tasks.hourly"
#     ],
#     "weekly": [
#         "selco.tasks.weekly"
#     ]
#     "monthly": [
#         "selco.tasks.monthly"
#     ]
# }

scheduler_events = {
    "daily": [
        'selco.selco_customizations.send_birthday_wishes',
        'selco.selco_customizations.send_po_reminder'
    ],
    "hourly": [
        "selco.selco_customizations.service_call_info"
    ],
}
# Testing
# -------

# before_tests = "selco.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
#     "frappe.desk.doctype.event.event.get_events": "selco.event.get_events"
# }
