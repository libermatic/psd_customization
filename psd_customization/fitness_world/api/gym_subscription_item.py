# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

import frappe


@frappe.whitelist()
def get_subscription_item(item_code):
    name = frappe.db.exists(
        'Gym Subscription Item', {'item': item_code},
    )
    return frappe.get_doc('Gym Subscription Item', name) if name else None
