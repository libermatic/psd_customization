# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

from psd_customization.fitness_world.doctype.gym_membership.gym_membership \
    import status_map
from psd_customization.fitness_world.api.gym_membership \
    import get_membership_by_subscription


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
        membership = get_membership_by_subscription(doc.name)
        membership.status = status_map.get(doc.status, membership.status)
        membership.save()
