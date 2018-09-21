# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import add_days, add_months, getdate
from erpnext.accounts.doctype.payment_entry.payment_entry \
    import get_payment_entry
from functools import partial
from toolz import pluck, compose, get, first

from psd_customization.utils.fp import pick


@frappe.whitelist()
def make_payment_entry(source_name):
    reference_invoice = frappe.db.get_value(
        'Gym Membership', source_name, 'reference_invoice'
    )
    return get_payment_entry('Sales Invoice', reference_invoice)


def _existing_membership(member):
    return frappe.db.sql(
        """
            SELECT to_date FROM `tabGym Membership`
            WHERE docstatus = 1 AND member = '{member}'
            ORDER BY to_date DESC
            LIMIT 1
        """.format(member=member),
        as_dict=True,
    )


@frappe.whitelist()
def get_next_from_date(member):
    existing_memberships = _existing_membership(member)
    if existing_memberships:
        return compose(
            partial(add_days, days=1),
            getdate,
            partial(get, 'to_date'),
            first,
        )(existing_memberships)
    return frappe.db.get_value('Gym Member', member, 'membership_start_date')


def get_to_date(from_date, frequency):
    make_end_of_freq = compose(
        partial(add_days, days=-1), partial(add_months, from_date)
    )
    freq_map = {
        'Monthly': 1,
        'Quaterly': 3,
        'Half-Yearly': 6,
        'Yearly': 12,
    }
    try:
        return make_end_of_freq(freq_map[frequency])
    except Exception as e:
        raise e


@frappe.whitelist()
def get_items(member, membership_plan):
    plan = frappe.get_doc('Gym Membership Plan', membership_plan)
    existing_memberships = _existing_membership(member)
    pick_fields = compose(
        partial(pick, ['item_code', 'item_name', 'qty', 'rate', 'amount']),
        lambda x: x.as_dict()
    )

    make_items = compose(
        partial(map, pick_fields),
        partial(filter, lambda x: not existing_memberships or not x.one_time),
    )
    return make_items(plan.items) if plan else None


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


def get_membership_by_invoice(invoice):
    invoices = frappe.db.sql(
        """
            SELECT name FROM `tabGym Membership`
            WHERE docstatus = 1 AND reference_invoice = '{invoice}'
        """.format(invoice=invoice),
        as_dict=True,
    )
    get_one_membership = compose(
        partial(frappe.get_doc, 'Gym Membership'),
        partial(get, 'name'),
        first,
    )
    return get_one_membership(invoices) if invoices else None


def generate_new_fees_on(posting_date):
    from psd_customization.fitness_world.api.gym_fee import (
        get_next_from_date, make_gym_fee
    )
    memberships = pluck('name', frappe.get_all(
        'Gym Membership',
        filters={
            'docstatus': 1,
            'status': 'Active',
            'auto_repeat': 'Yes',
        }
    ))
    do_not_submit = not frappe.db.get_value(
        'Gym Settings', None, 'submit_auto_fees'
    )
    for membership in memberships:
        if get_next_from_date(membership) == getdate(posting_date):
            fee = make_gym_fee(membership, posting_date, do_not_submit)
            frappe.logger(__name__).debug(
                'Gym Fee {} ({}) generated'.format(fee.name, posting_date)
            )
