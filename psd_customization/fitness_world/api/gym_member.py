# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from erpnext.accounts.party import get_party_account
from erpnext.accounts.doctype.payment_entry.payment_entry \
    import get_payment_entry
from toolz import pluck, compose, first, drop


def get_member_contacts(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql(
        """
            SELECT `tabContact`.name
            FROM `tabContact`, `tabDynamic Link`
            WHERE
                `tabContact`.name = `tabDynamic Link`.parent AND
                `tabDynamic Link`.link_name = %(member)s AND
                `tabDynamic Link`.link_doctype = 'Gym Member'
        """, {
            'member': filters.get('member'),
        })


@frappe.whitelist()
def link_member_to_doctype(member, doctype, docname):
    link_doc = frappe.get_doc(doctype, docname)
    if link_doc:
        make_links = compose(
            partial(map, lambda x: x.get('link_name')),
            partial(filter, lambda x: x.get('link_doctype') == 'Gym Member'),
        )
        if member not in make_links(link_doc.links):
            link_doc.append('links', {
                'link_doctype': 'Gym Member', 'link_name': member
            })
            link_doc.save()
    return link_doc


def _make_new_pe(member):
    pe = frappe.new_doc('Payment Entry')
    pe.payment_type = 'Receive'
    pe.party_type = 'Customer'
    pe.party = member.customer
    pe.party_name = member.member_name
    company = frappe.db.get_value('Gym Settings', None, 'default_company')
    pe.party_account = get_party_account('Customer', member.customer, company)
    pe.paid_from = pe.party_account
    return pe


@frappe.whitelist()
def make_payment_entry(source_name):
    member = frappe.get_doc('Gym Member', source_name)
    invoices = frappe.get_all(
        'Sales Invoice',
        filters=[
            ['customer', '=', member.customer],
            ['docstatus', '=', '1'],
            ['status', '!=', 'Paid'],
        ],
    )
    pes = compose(
        partial(map, lambda x: get_payment_entry('Sales Invoice', x)),
        partial(pluck, 'name'),
    )(invoices)
    pe = first(pes) if pes else _make_new_pe(member)
    for entry in drop(1, pes):
        pe.set(
            'paid_amount', pe.paid_amount + entry.paid_amount
        )
        pe.set(
            'received_amount', pe.received_amount + entry.received_amount
        )
        for ref in entry.references:
            pe.append('references', ref)
    pe.set_amounts()
    return pe


@frappe.whitelist()
def get_members_by_customer(customer):
    members = frappe.get_all('Gym Member', filters={'customer': customer})
    return map(lambda x: x.get('name'), members)


@frappe.whitelist()
def set_auto_renew(name, auto_renew):
    try:
        member = frappe.get_doc('Gym Member', name)
        member.auto_renew = auto_renew
        member.save()
    except AttributeError:
        pass
