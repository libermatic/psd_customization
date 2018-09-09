# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
# from frappe.utils import formatdate
# from frappe.contacts.doctype.contact.contact import get_default_contact
# from frappe.core.doctype.sms_settings.sms_settings \
#     import get_contact_number, send_sms
#
# from psd_customization.fitness_world.doctype.gym_sms_template.\
#     gym_sms_template import get_sms_text
# from psd_customization.fitness_world.doctype.gym_membership.\
#     gym_membership import get_expiry_date, is_gym_customer
# from psd_customization.fitness_world.api.gym_membership \
#     import get_membership_by_subscription
#
#
# def _make_template_data(doc, frequency):
#     end_date = get_expiry_date(doc.posting_date, frequency)
#     period = doc.get_formatted('posting_date') \
#         if doc.posting_date == end_date else \
#         '{} - {}'.format(
#             doc.get_formatted('posting_date'), formatdate(end_date)
#         )
#     return {
#         'customer_name': doc.customer_name,
#         'sales_invoice': doc.name,
#         'amount': doc.get_formatted('rounded_total'),
#         'period': period,
#         'due_date': doc.get_formatted('due_date'),
#     }
#
#
# def on_submit_or_cancel(doc, method):
#     if doc.party_type == 'Customer' and is_gym_customer(doc.party):
#         paid_invoices = frappe.db.sql(
#             '''
#                 SELECT name, posting_date, subscription
#                 FROM `tabSales Invoice`
#                 WHERE docstatus = 1 AND
#                     status = 'Paid' AND
#                     customer = '{customer}' AND
#                     IFNULL(subscription, '') != ''
#                 GROUP BY subscription
#                 ORDER BY posting_date DESC
#             '''.format(customer=doc.party),
#             as_dict=1,
#         )
#         for item in paid_invoices:
#             si = frappe._dict(item)
#             membership = get_membership_by_subscription(si.subscription)
#             frequency = frappe.db.get_value(
#                 'Subscription', si.subscription, 'frequency'
#             )
#             if membership:
#                 membership.update_expiry_date(
#                     get_expiry_date(si.posting_date, frequency),
#                     force=(method == 'on_cancel'),
#                 )
#         if method == 'on_submit':
#             contact_person = get_default_contact('Customer', doc.party)
#             if contact_person:
#                 mobile_no = get_contact_number(
#                     contact_person, 'Customer', doc.party,
#                 )
#                 template = frappe.db.get_value(
#                     'Gym Settings', None, 'sms_receipt'
#                 )
#                 text = get_sms_text(
#                     template,
#                     _make_template_data(doc, frequency),
#                 )
#                 if mobile_no and text:
#                     # fix for json.loads casting to int during num validation
#                     send_sms('"{}"'.format(mobile_no), text)


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
