# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

from psd_customization.fitness_world.api.gym_subscription \
    import get_subscription_by_invoice


def on_submit_or_cancel(doc, method):
    for ref in doc.references:
        if ref.reference_doctype == 'Sales Invoice':
            subscription = get_subscription_by_invoice(ref.reference_name)
            if subscription:
                status = frappe.db.get_value(
                    'Sales Invoice', ref.reference_name, 'status'
                )
                subscription.status = 'Paid' if status == 'Paid' else 'Unpaid'
                subscription.save()
