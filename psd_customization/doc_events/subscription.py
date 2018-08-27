# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _


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
