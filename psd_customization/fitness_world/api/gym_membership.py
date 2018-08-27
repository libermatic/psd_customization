# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry \
    import get_payment_entry
from functools import partial
from toolz import pluck, compose, first, drop


def _make_new_pe(membership):
    pe = frappe.new_doc('Payment Entry')
    pe.payment_type = 'Receive'
    pe.party_type = 'Customer'
    pe.party = membership.customer
    pe.party_name = membership.member_name
    return pe


@frappe.whitelist()
def make_payment_entry(source_name):
    membership = frappe.get_doc('Gym Membership', source_name)
    invoices = frappe.get_all(
        'Sales Invoice',
        filters=[
            ['customer', '=', membership.customer],
            ['docstatus', '=', '1'],
            ['status', '!=', 'Paid'],
        ],
    )
    pes = compose(
        partial(map, lambda x: get_payment_entry('Sales Invoice', x)),
        partial(pluck, 'name'),
    )(invoices)
    pe = first(pes) if pes else _make_new_pe(membership)
    for entry in drop(1, pes):
        pe.set(
            'paid_amount', pe.paid_amount + entry.paid_amount
        )
        pe.set(
            'received_amount', pe.received_amount + entry.received_amount
        )
        for ref in entry.references:
            pe.append('references', ref)
    if pe.party_account:
        pe.set_amounts()
    return pe
