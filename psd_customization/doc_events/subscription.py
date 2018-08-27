# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.utils import add_days


def on_submit(doc, method):
    if doc.reference_gym_member:
        membership = frappe.get_doc({
            'doctype': 'Gym Membership',
            'member': doc.reference_gym_member,
            'status': 'Active',
            'start_date': doc.start_date,
            'end_date': doc.end_date,
            'frequency': doc.frequency,
            'subscription': doc.name,
        })
        si = frappe.get_doc('Sales Invoice', doc.reference_document)
        if si:
            for item in si.items:
                membership.append('items', {
                    'item_code': item.item_code,
                    'item_name': item.item_name,
                })
        membership.insert()
        membership.submit()


def on_update_after_submit(doc, method):
    status_map = {
        'Submitted': 'Active',
        'Cancelled': 'Cancelled',
    }
    if doc.reference_gym_member:
        membership = frappe.get_doc(
            'Gym membership', filters={'subscription': doc.name}
        )
        if membership:
            membership.status = status_map.get(doc.status, membership.status)
            membership.expiry_date = add_days(doc.next_schedule_date, -1)
            membership.save()
