# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import add_days, add_months, add_years, today
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


def get_end_date(start_date, frequency, times=1):
    if times < 1:
        raise Exception('times cannot be less than 1')
    if frequency == 'Daily':
        return add_days(start_date, times - 1)
    if frequency == 'Weekly':
        return add_days(start_date, times * 7 - 1)
    if frequency == 'Monthly':
        return add_days(add_months(start_date, times), -1)
    if frequency == 'Quaterly':
        return add_days(add_months(start_date, times * 3), -1)
    if frequency == 'Half-Yearly':
        return add_days(add_months(start_date, times * 6), -1)
    if frequency == 'Yearly':
        return add_days(add_years(start_date, times), -1)
    return None


@frappe.whitelist()
def get_item_price(item_code, price_list='Standard Selling'):
    prices = frappe.db.sql(
        """
            SELECT price_list_rate
            FROM `tabItem Price`
            WHERE
                price_list = '{price_list}' AND
                item_code = '{item_code}'
        """.format(item_code=item_code, price_list=price_list)
    )
    if prices:
        return prices[0][0]
    return 0


@frappe.whitelist()
def stop(name, end_date=today()):
    membership = frappe.get_doc('Gym Membership', name)
    if membership:
        membership.status = 'Stopped'
        membership.end_date = end_date
        membership.save()


@frappe.whitelist()
def resume(name):
    membership = frappe.get_doc('Gym Membership', name)
    if membership:
        membership.status = 'Active'
        membership.end_date = None
        membership.save()
