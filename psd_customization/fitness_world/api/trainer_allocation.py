# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, add_days

from functools import partial
from toolz import pluck, compose


@frappe.whitelist()
def get_trainable_items(subscription):
    doc = frappe.get_doc('Gym Subscription', subscription)
    if not doc:
        frappe.throw('Gym Subscription: {} not found'.format(subscription))
    all_training_items = frappe.get_all(
        'Item',
        filters={
            'item_group': frappe.db.get_value(
                'Gym Settings', None, 'default_item_group'
            ),
            'is_gym_subscription_item': 1,
        }
    )
    items = compose(
        partial(map, lambda x: x.item_name),
        partial(
            filter, lambda x: x.item_code in pluck('name', all_training_items)
        ),
    )(doc.service_items)
    if not items:
        return None
    return {
        'items': items,
        'from_date': doc.from_date,
        'to_date': doc.to_date,
    }


def _generate_intervals(start_date, end_date, allocations):
    if not allocations:
        return [{'from_date': start_date, 'to_date': end_date}]
    intervals = []
    cur_start = start_date
    for a in allocations:
        if getdate(cur_start) < getdate(a.get('from_date')):
            intervals.append({
                'from_date': cur_start,
                'to_date': add_days(a.get('from_date'), -1),
            })
        intervals.append(a)
        cur_start = add_days(a.get('to_date'), 1)
    if getdate(intervals[-1]['to_date']) < getdate(end_date):
        intervals.append({
            'from_date': add_days(intervals[-1]['to_date'], 1),
            'to_date': end_date,
        })
    return intervals


@frappe.whitelist()
def get_schedule(subscription, item=None):
    sub_start, sub_end = frappe.db.get_value(
        'Gym Subscription', subscription, ['from_date', 'to_date']
    )
    allocations = frappe.get_all(
        'Trainer Allocation',
        filters={'gym_subscription': subscription},
        fields={'name', 'gym_trainer', 'from_date', 'to_date', 'training_slot'}
    )
    return _generate_intervals(sub_start, sub_end, allocations)


@frappe.whitelist()
def create(subscription, trainer, from_date, to_date):
    allocation = frappe.get_doc({
        'doctype': 'Trainer Allocation',
        'gym_subscription': subscription,
        'gym_trainer': trainer,
        'from_date': from_date,
        'to_date': to_date,
    }).insert()
    return allocation


def _get_field(key):
    if key == 'slot':
        return 'training_slot'
    if key in ['from_date', 'to_date']:
        return key
    return None


@frappe.whitelist()
def update(name, key, value):
    allocation = frappe.get_doc('Trainer Allocation', name)
    field = _get_field(key)
    if field:
        allocation.set_value(field, value)
        allocation.save()
    return allocation


@frappe.whitelist()
def remove(name):
    return frappe.delete_doc('Trainer Allocation', name)
