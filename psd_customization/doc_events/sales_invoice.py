# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.utils import add_days, add_months, add_years, formatdate
from frappe.core.doctype.sms_settings.sms_settings \
    import get_contact_number, send_sms

from psd_customization.fitness_world.doctype.gym_sms_template.\
    gym_sms_template import get_sms_text


def _make_template_data(doc, frequency):
    def get_period():
        if frequency == 'Daily':
            return doc.get_formatted('posting_date')
        if frequency == 'Weekly':
            return '{} - {}'.format(
                doc.get_formatted('posting_date'),
                formatdate(add_days(doc.posting_date, 6))
            )
        if frequency == 'Monthly':
            return '{} - {}'.format(
                doc.get_formatted('posting_date'),
                formatdate(add_days(add_months(doc.posting_date, 1), -1))
            )
        if frequency == 'Quaterly':
            return '{} - {}'.format(
                doc.get_formatted('posting_date'),
                formatdate(add_days(add_months(doc.posting_date, 3), -1))
            )
        if frequency == 'Half-Yearly':
            return '{} - {}'.format(
                doc.get_formatted('posting_date'),
                formatdate(add_days(add_months(doc.posting_date, 6), -1))
            )
        if frequency == 'Yearly':
            return '{} - {}'.format(
                doc.get_formatted('posting_date'),
                formatdate(add_years(doc.posting_date, 1))
            )
        return None
    return {
        'customer_name': doc.customer_name,
        'sales_invoice': doc.name,
        'amount': doc.get_formatted('rounded_total'),
        'period': get_period(),
        'due_date': doc.get_formatted('due_date'),
    }


def on_submit(doc, method):
    if doc.subscription:
        if doc.contact_person:
            mobile_no = get_contact_number(
                doc.contact_person, 'Customer', doc.customer,
            )
            template = frappe.db.get_value(
                'Gym Settings', None, 'sms_invoiced'
            )
            frequency = frappe.db.get_value(
                'Subscription', doc.subscription, 'frequency'
            )
            text = get_sms_text(
                template,
                _make_template_data(doc, frequency),
            )
            if mobile_no and text:
                # fix for json.loads casting to int during number validation
                send_sms('"{}"'.format(mobile_no), text)
