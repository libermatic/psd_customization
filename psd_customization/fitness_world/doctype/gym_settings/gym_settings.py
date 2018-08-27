# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class GymSettings(Document):
    pass


def get_sms_text(type, doc):
    template = frappe.db.get_value(
        'Gym Settings', None, 'sms_{}'.format(type)
    )
    if not template:
        return
    return frappe.render_template(template, {'doc': doc})
