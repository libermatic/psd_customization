# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _


def before_save(doc, method):
    has_expiry_date = frappe.db.get_value('Item', doc.item, 'has_expiry_date')
    if has_expiry_date and not doc.expiry_date:
        frappe.throw(_('Expiry date is mandatory for selected item'))


def autoname(doc, method):
    name_args = []
    if doc.expiry_date:
        expiry_date = frappe.utils.getdate(doc.expiry_date)
        name_args.append('{:%m%y}'.format(expiry_date))
    name_args.append(doc.item)
    # '0' because fixtures set default to this value
    if doc.batch_id != '0':
        name_args.append(doc.batch_id)
    doc.name = '/'.join(name_args)
    if doc.batch_id == '0':
        doc.batch_id = doc.name
