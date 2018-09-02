# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.utils import formatdate
from frappe.core.doctype.sms_settings.sms_settings \
    import get_contact_number, send_sms

from psd_customization.fitness_world.doctype.gym_sms_template.\
    gym_sms_template import get_sms_text
from psd_customization.fitness_world.doctype.gym_membership.\
    gym_membership import get_expiry_date, is_gym_customer
from psd_customization.fitness_world.api.gym_membership \
    import get_membership_by_subscription


def _make_template_data(doc, frequency):
    end_date = get_expiry_date(doc.posting_date, frequency)
    period = doc.get_formatted('posting_date') \
        if doc.posting_date == end_date else \
        '{} - {}'.format(
            doc.get_formatted('posting_date'), formatdate(end_date)
        )
    return {
        'customer_name': doc.customer_name,
        'sales_invoice': doc.name,
        'amount': doc.get_formatted('rounded_total'),
        'period': period,
        'due_date': doc.get_formatted('due_date'),
    }


def on_submit(doc, method):
    if is_gym_customer(doc.customer) and doc.subscription:
        membership = get_membership_by_subscription(doc.subscription)
        frequency = frappe.db.get_value(
            'Subscription', doc.subscription, 'frequency'
        )
        if doc.status == 'Paid' and membership:
            membership.update_expiry_date(
                get_expiry_date(doc.posting_date, frequency)
            )

        if doc.contact_person:
            mobile_no = get_contact_number(
                doc.contact_person, 'Customer', doc.customer,
            )
            template = frappe.db.get_value(
                'Gym Settings', None, 'sms_invoiced'
            )
            text = get_sms_text(
                template,
                _make_template_data(doc, frequency),
            )
            if mobile_no and text:
                # fix for json.loads casting to int during number validation
                send_sms('"{}"'.format(mobile_no), text)
