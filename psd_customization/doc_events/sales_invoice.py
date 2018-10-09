# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


def validate(doc, method):
    if doc.gym_subscription:
        reference_invoice = frappe.db.get_value(
            'Gym Subscription', doc.gym_subscription, 'reference_invoice',
        )
        if reference_invoice:
            frappe.throw(
                'Subscription {subscription} is already connected to another '
                'Sales Invoice: {sales_invoice}'.format(
                    subscription=doc.gym_subscription,
                    sales_invoice=reference_invoice,
                )
            )


def on_submit(doc, method):
    if doc.gym_subscription:
        subscription = frappe.get_doc('Gym Subscription', doc.gym_subscription)
        subscription.reference_invoice = doc.name
        subscription.status = 'Paid' if doc.status == 'Paid' else 'Unpaid'
        subscription.save()


def on_cancel(doc, method):
    if doc.gym_subscription:
        subscription = frappe.get_doc('Gym Subscription', doc.gym_subscription)
        if subscription and subscription.docstatus == 1:
            subscription.cancel()
