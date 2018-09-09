# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


from psd_customization.fitness_world.api.gym_fee import get_fee_by_invoice


def on_submit_or_cancel(doc, method):
    for ref in doc.references:
        if ref.reference_doctype == 'Sales Invoice':
            fee = get_fee_by_invoice(ref.reference_name)
            if fee:
                status = frappe.db.get_value(
                    'Sales Invoice', ref.reference_name, 'status'
                )
                fee.status = 'Paid' if status == 'Paid' else 'Unpaid'
                fee.save()
