# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.contacts.address_and_contact import load_address_and_contact
from frappe.contacts.doctype.address.address import get_default_address
from frappe.contacts.doctype.contact.contact import get_default_contact
from psd_customization.utils.fp import pick, compact
from toolz import merge


class GymMember(Document):
    def onload(self):
        load_address_and_contact(self)

    def before_save(self):
        self.flags.is_new_doc = self.is_new()
        self.member_name = ' '.join(
            compact([self.first_name, self.last_name])
        )

    def on_update(self):
        if self.flags.is_new_doc:
            if not self.customer:
                customer = create_customer(self)
                self.customer = customer.name
                self.save()
            self.fetch_and_link_doc('Address', get_default_address)
            self.fetch_and_link_doc('Contact', get_default_contact)

    def fetch_and_link_doc(self, doctype, fetch_fn):
        docname = fetch_fn('Customer', self.customer)
        if docname:
            doc = frappe.get_doc(doctype, docname)
            doc.append('links', {
                'link_doctype': 'Gym Member',
                'link_name': self.name,
            })
            doc.save()


def create_customer(doc):
    field_kwargs = pick([
        'email_id', 'mobile_no',
        'address_line1', 'address_line2',
        'city', 'state', 'pincode', 'country',
    ], doc)
    customer_group = frappe.get_value(
        'Gym Settings', None, 'default_customer_group'
    )
    return frappe.get_doc(
        merge({
            'doctype': 'Customer',
            'customer_name': doc.member_name,
            'customer_type': 'Individual',
            'customer_group': customer_group or 'All Customer Groups',
            'territory': 'All Territories',
        }, field_kwargs)
    ).insert()
