# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


def validate(doc, method):
    if doc.gym_membership:
        reference_invoice = frappe.db.get_value(
            'Gym Membership', doc.gym_membership, 'reference_invoice',
        )
        if reference_invoice:
            frappe.throw(
                'Membership {membership} is already connected to another '
                'Sales Invoice: {sales_invoice}'.format(
                    membership=doc.gym_membership,
                    sales_invoice=reference_invoice,
                )
            )


def on_submit(doc, method):
    if doc.gym_membership:
        membership = frappe.get_doc('Gym Membership', doc.gym_membership)
        membership.reference_invoice = doc.name
        membership.status = 'Paid' if doc.status == 'Paid' else 'Unpaid'
        membership.save()


def on_cancel(doc, method):
    if doc.gym_membership:
        membership = frappe.get_doc('Gym Membership', doc.gym_membership)
        if membership and membership.docstatus == 1:
            membership.cancel()
