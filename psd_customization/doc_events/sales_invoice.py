# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.utils import cint
from functools import partial
from toolz import compose

from psd_customization.fitness_world.api.gym_subscription_item \
    import get_subscription_item
from psd_customization.fitness_world.api.gym_subscription \
    import validate_dependencies


def validate(doc, method):
    filter_and_make_items = compose(
        partial(
            map,
            lambda x: frappe._dict({
                'item_code': x.item_code,
                'item_name': x.item_name,
                'from_date': x.gym_from_date,
                'to_date': x.gym_to_date,
                'is_lifetime': x.gym_is_lifetime,
            }),
        ),
        # this is excluded because existing Subscriptions are assumed to be
        # already validated
        partial(filter, lambda x: not x.gym_subscription),
        partial(filter, lambda x: cint(x.is_gym_subscription)),
    )
    if doc.gym_member:
        validate_dependencies(
            doc.gym_member, filter_and_make_items(doc.items)
        )


def on_submit(doc, method):
    if doc.gym_member:
        subs = []
        for item in doc.items:
            if item.is_gym_subscription:
                if item.gym_subscription:
                    sub = frappe.get_doc(
                        'Gym Subscription', item.gym_subscription
                    )
                    if sub and not sub.reference_invoice:
                        sub.reference_invoice = doc.name
                        sub.save(ignore_permissions=True)
                        subs.append(sub.name)
                else:
                    sub_item = get_subscription_item(item.item_code)
                    if sub_item:
                        sub = _make_subscription(item, sub_item, doc)
                        sub.flags.source_doc = 'Sales Invoice'
                        sub.insert(ignore_permissions=True)
                        sub.submit()
                        frappe.db.set_value(
                            'Sales Invoice Item',
                            item.name,
                            'gym_subscription',
                            sub.name,
                        )
                        subs.append(sub.name)
        if subs:
            frappe.msgprint(
                'Gym Subscription(s) {} linked.'.format(', '.join(subs))
            )
        doc.reload()


def _make_subscription(item, sub_item, invoice):
    return frappe.get_doc({
        'doctype': 'Gym Subscription',
        'member': invoice.gym_member,
        'member_name': invoice.gym_member_name,
        'posting_date': invoice.posting_date,
        'reference_invoice': invoice.name,
        'subscription_item': sub_item.name,
        'subscription_name': sub_item.item_name,
        'is_lifetime': item.gym_is_lifetime,
        'from_date': item.gym_from_date,
        'to_date': item.gym_to_date,
    })


def on_cancel(doc, method):
    if doc.gym_member:
        subs = []
        for item in doc.items:
            if item.is_gym_subscription and item.gym_subscription:
                sub = frappe.get_doc(
                    'Gym Subscription', item.gym_subscription
                )
                if sub and sub.docstatus == 1:
                    sub.reference_invoice = None
                    sub.save(ignore_permissions=True)
                    subs.append(item.gym_subscription)
                frappe.db.set_value(
                    'Sales Invoice Item', item.name, 'gym_subscription', None,
                )
        if subs:
            frappe.msgprint(
                'Gym Subscription(s) {} removed from Sales Invoice.'.format(
                    ', '.join(subs)
                )
            )
