# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


status_map = {
    'Submitted': 'Active',
    'Stopped': 'Stopped',
    'Cancelled': 'Cancelled',
    'Completed': 'Stopped',
}


class GymMembership(Document):
    def before_submit(self):
        subscription = frappe.get_doc('Subscription', self.subscription)
        if subscription.docstatus != 1:
            return frappe.throw(
                'Subscription {} has a status of {}'.format(
                    self.subscription, subscription.status
                )
            )
        self.status = status_map.get(subscription.status)
        self.start_date = subscription.start_date
        self.end_date = subscription.end_date
        self.frequency = subscription.frequency
        si = frappe.get_doc('Sales Invoice', subscription.reference_document)
        if si:
            for item in si.items:
                self.append('items', {
                    'item_code': item.item_code,
                    'item_name': item.item_name,
                })
