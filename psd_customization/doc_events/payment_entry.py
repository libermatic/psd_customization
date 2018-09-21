# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

from psd_customization.fitness_world.api.gym_membership \
    import get_membership_by_invoice


def on_submit_or_cancel(doc, method):
    for ref in doc.references:
        if ref.reference_doctype == 'Sales Invoice':
            membership = get_membership_by_invoice(ref.reference_name)
            if membership:
                status = frappe.db.get_value(
                    'Sales Invoice', ref.reference_name, 'status'
                )
                membership.status = 'Paid' if status == 'Paid' else 'Unpaid'
                membership.save()
