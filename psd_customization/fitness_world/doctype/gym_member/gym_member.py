# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.contacts.address_and_contact \
    import load_address_and_contact, delete_contact_and_address
from frappe.utils import today
import operator
from functools import reduce
from toolz import count, pluck

from psd_customization.utils.fp import pick


class GymMember(Document):
    def onload(self):
        load_address_and_contact(self)
        self.load_subscription_details()

    def validate(self):
        if not self.is_new() and not self.enrollment_date:
            frappe.throw('Enrollment Date cannot be empty.')

    def before_save(self):
        self.flags.is_new_doc = self.is_new()
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
            self.make_contact_and_address(
                pick([
                    'email_id', 'mobile_no',
                    'address_line1', 'address_line2',
                    'city', 'state', 'pincode', 'country',
                ], self)
            )

    def on_trash(self):
        # clears notification_contact for LinkExistsException
        self.db_set('notification_contact', None)
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

    def make_contact_and_address(self, args, is_primary_contact=1):
        if any(field in args.keys() for field in ['email_id', 'mobile_no']):
            contact = frappe.get_doc({
                'doctype': 'Contact',
                'first_name': self.member_name,
                'email_id': args.get('email_id'),
                'mobile_no': args.get('mobile_no'),
                'is_primary_contact': is_primary_contact,
                'links': [{
                    'link_doctype': 'Gym Member',
                    'link_name': self.name,
                }],
            }).insert()
            # sets notification_contact and number
            self.db_set('notification_contact', contact.name)
            self.db_set('notification_number', contact.mobile_no)
        if all(field in args.keys() for field in ['address_line1', 'city']):
            frappe.get_doc({
                'doctype': 'Address',
                'address_title': self.member_name,
                'address_type': 'Personal',
                'address_line1': args.get('address_line1'),
                'address_line2': args.get('address_line2'),
                'city': args.get('city'),
                'state': args.get('state'),
                'pincode': args.get('pincode'),
                'country': args.get('country'),
                'links': [{
                    'link_doctype': 'Gym Member',
                    'link_name': self.name,
                }],
            }).insert()
        print('done')

    def create_customer(self):
        customer_group = frappe.get_value(
            'Gym Settings', None, 'default_customer_group'
        )
        customer = frappe.get_doc({
            'doctype': 'Customer',
            'customer_name': self.member_name,
            'customer_type': 'Individual',
            'customer_group': customer_group or 'All Customer Groups',
            'territory': 'All Territories',
        }).insert()
        return customer.name
