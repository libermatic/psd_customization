# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import add_days, add_months, add_years, date_diff


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
        self.expiry_date = get_expiry_date(
            subscription.start_date, subscription.frequency
        )
        self.end_date = subscription.end_date
        self.frequency = subscription.frequency
        self.items = []
        si = frappe.get_doc('Sales Invoice', subscription.reference_document)
        if si:
            for item in si.items:
                self.append('items', {
                    'item_code': item.item_code,
                    'item_name': item.item_name,
                })

    def before_cancel(self):
        self.status = 'Cancelled'

    def on_cancel(self):
        subscription = frappe.get_doc('Subscription', self.subscription)
        subscription.cancel()

    def update_expiry_date(self, expiry_date):
        if date_diff(expiry_date, self.expiry_date) > 0:
            self.expiry_date = expiry_date
            self.save()


def get_expiry_date(posting_date, frequency):
    if frequency == 'Daily':
        return posting_date
    if frequency == 'Weekly':
        return add_days(posting_date, 6)
    if frequency == 'Monthly':
        return add_days(add_months(posting_date, 1), -1)
    if frequency == 'Quaterly':
        return add_days(add_months(posting_date, 3), -1)
    if frequency == 'Half-Yearly':
        return add_days(add_months(posting_date, 6), -1)
    if frequency == 'Yearly':
        return add_years(posting_date, 1)
    return None


def is_gym_customer(customer):
    gym_member_group = frappe.db.get_value(
        'Gym Settings', None, 'default_customer_group'
    )
    customer_group = frappe.db.get_value(
        'Customer', customer, 'customer_group'
    )
    return gym_member_group == customer_group
