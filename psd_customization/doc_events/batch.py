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
        name_args.append(doc.expiry_date)
    name_args.append(doc.item)
    if doc.batch_id:
        name_args.append(doc.batch_id)
    doc.name = '/'.join(name_args)
    if not doc.batch_id:
        doc.batch_id = doc.name
