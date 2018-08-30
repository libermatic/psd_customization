# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.utils import add_days

from psd_customization.fitness_world.doctype.gym_membership.gym_membership \
    import status_map


def on_submit(doc, method):
    if doc.reference_gym_member:
        membership = frappe.get_doc({
            'doctype': 'Gym Membership',
            'member': doc.reference_gym_member,
            'subscription': doc.name,
        })
        membership.insert()
        membership.submit()


def on_update_after_submit(doc, method):
    if doc.reference_gym_member:
        membership_name = frappe.db.get_value(
            'Gym Membership', filters={'subscription': doc.name}
        )
        if membership_name:
            membership = frappe.get_doc('Gym Membership', membership_name)
            membership.status = status_map.get(doc.status, membership.status)
            membership.expiry_date = add_days(doc.next_schedule_date, -1)
            membership.save()
