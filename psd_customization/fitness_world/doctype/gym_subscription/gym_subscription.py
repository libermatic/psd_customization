# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, flt
from frappe.model.document import Document
from functools import reduce, partial
from toolz import pluck

from psd_customization.fitness_world.api.gym_membership import (
    get_membership_by,
)
from psd_customization.fitness_world.api.gym_subscription import (
    dispatch_sms, make_sales_invoice,
    get_existing_subscription, has_valid_subscription,
)


class GymSubscription(Document):
    def onload(self):
        if self.reference_invoice and self.docstatus == 1:
            rounded_total, status = frappe.db.get_value(
                'Sales Invoice',
                self.reference_invoice,
                ['rounded_total', 'status'],
            )
            self.set_onload('si_value', rounded_total)
            self.set_onload('si_status', status)

    def validate(self):
        if not self.membership_items and not self.service_items:
            frappe.throw('Cannot create Subscription without any items')
        if not self.membership_items and \
                not get_membership_by(
                    self.member, self.from_date, self.to_date
                ):
            frappe.throw('Cannot create Subscription without Membership')
        if self.service_items:
            self.validate_service_dependencies()

    def validate_service_dependencies(self):
        subscription_exists = partial(
            get_existing_subscription,
            member=self.member,
            start_date=self.from_date,
            end_date=self.to_date,
        )
        dependency_exists = partial(
            has_valid_subscription,
            member=self.member,
            start_date=self.from_date,
            end_date=self.to_date,
        )
        for item in self.service_items:
            existing = subscription_exists(item_code=item.item_code)
            if existing:
                frappe.throw(
                    'Another Subscription - {subscription}, for {item_code}'
                    ' already exists during this time frame.'.format(
                        subscription=existing.get('subscription'),
                        item_code=item.item_name
                    )
                )
            for p in pluck(
                'item',
                frappe.get_all(
                    'Gym Item Parent',
                    fields=['item'],
                    filters={
                        'parent': item.item_code,
                        'parentfield': 'gym_parent_items',
                        'parenttype': 'Item',
                    }
                ),
            ):
                if p not in map(lambda x: x.item_code, self.service_items) \
                        and not dependency_exists(item_code=p):
                    p_name = frappe.db.get_value('Item', p, 'item_name')
                    frappe.throw(
                        'Required dependency {} not fulfiled.'.format(p_name)
                    )

    def before_save(self):
        self.total_amount = reduce(
            lambda a, x: a + flt(x.amount),
            self.membership_items + self.service_items,
            0
        )

    def on_submit(self):
        if not cint(self.no_invoice):
            self.reference_invoice = self.create_sales_invoice()

    def on_update_after_submit(self):
        if self.status == 'Paid':
            dispatch_sms(self.name, 'sms_receipt')

    def on_cancel(self):
        if self.reference_invoice:
            si = frappe.get_doc('Sales Invoice', self.reference_invoice)
            if si.docstatus == 1:
                si.cancel()

    def create_sales_invoice(self):
        si = make_sales_invoice(self.name)
        si.set_posting_time = 1
        si.posting_date = self.posting_date
        si.due_date = None
        si.payment_terms_template = frappe.db.get_value(
            'Gym Settings', None, 'default_payment_template'
        )
        si.insert()
        si.submit()
        return si.name
