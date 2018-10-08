# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.contacts.address_and_contact \
    import load_address_and_contact, delete_contact_and_address
from frappe.contacts.doctype.address.address import get_default_address
from frappe.contacts.doctype.contact.contact import get_default_contact
from frappe.utils import today
import operator
from functools import reduce
from toolz import merge, count, pluck

from psd_customization.utils.fp import pick, compact


class GymMember(Document):
    def onload(self):
        load_address_and_contact(self)
        self.load_subscription_details()

    def validate(self):
        if not self.is_new() and not self.enrollment_date:
            frappe.throw('Enrollment Date cannot be empty.')

    def before_save(self):
        self.flags.is_new_doc = self.is_new()
        self.member_name = ' '.join(
            compact([self.first_name, self.last_name])
        )
        if self.is_new() and not self.enrollment_date:
            self.enrollment_date = today()
        if not self.status:
            self.status = 'Active'
        if not self.auto_renew:
            self.auto_renew = 'No'
        if not self.customer:
            self.customer = self.create_customer()
        if not self.notification_contact:
            self.notification_number = None

    def on_update(self):
        if self.flags.is_new_doc:
            self.fetch_and_link_doc('Address', get_default_address)
            self.notification_contact = \
                self.fetch_and_link_doc('Contact', get_default_contact)
            self.save()

    def on_trash(self):
        delete_contact_and_address('Gym Member', self.name)

    def after_delete(self):
        frappe.delete_doc('Customer', self.customer)

    def load_subscription_details(self):
        all_subscriptions = frappe.db.sql(
            """
                SELECT
                    si.rounded_total AS amount,
                    ms.status AS status,
                    ms.to_date AS end_date
                FROM `tabGym Subscription` AS ms, `tabSales Invoice` AS si
                WHERE
                    ms.docstatus = 1 AND
                    ms.member = '{member}' AND
                    ms.reference_invoice = si.name
                ORDER BY ms.to_date DESC
            """.format(member=self.name),
            as_dict=True,
        )
        unpaid_subscriptions = filter(
            lambda x: x.get('status') == 'Unpaid', all_subscriptions
        )
        outstanding = reduce(
            operator.add, pluck('amount', unpaid_subscriptions), 0
        )
        self.set_onload('subscription_details', {
            'total_invoices': count(all_subscriptions),
            'unpaid_invoices': count(unpaid_subscriptions),
            'outstanding': outstanding,
        })

        all_subscription_items = frappe.db.sql(
            """
                SELECT
                    mi.item_code AS item_code,
                    mi.item_name AS item_name,
                    MAX(mi.end_date) AS expiry_date,
                    ms.name AS subscription,
                    ms.status AS status
                FROM
                    `tabGym Subscription Item` AS mi,
                    `tabGym Subscription` AS ms
                WHERE
                    mi.one_time != 1 AND
                    ms.member = '{member}' AND
                    ms.docstatus = 1 AND
                    ms.name = mi.parent
                GROUP BY
                    mi.item_code
            """.format(member=self.name),
            as_dict=1,
        )
        self.set_onload('subscription_items', all_subscription_items)

    def fetch_and_link_doc(self, doctype, fetch_fn):
        docname = fetch_fn('Customer', self.customer)
        if docname:
            doc = frappe.get_doc(doctype, docname)
            doc.append('links', {
                'link_doctype': 'Gym Member',
                'link_name': self.name,
            })
            doc.save()
        return docname

    def create_customer(self):
        field_kwargs = pick([
            'email_id', 'mobile_no',
            'address_line1', 'address_line2',
            'city', 'state', 'pincode', 'country',
        ], self)
        customer_group = frappe.get_value(
            'Gym Settings', None, 'default_customer_group'
        )
        customer = frappe.get_doc(
            merge({
                'doctype': 'Customer',
                'customer_name': self.member_name,
                'customer_type': 'Individual',
                'customer_group': customer_group or 'All Customer Groups',
                'territory': 'All Territories',
            }, field_kwargs)
        ).insert()
        return customer.name
