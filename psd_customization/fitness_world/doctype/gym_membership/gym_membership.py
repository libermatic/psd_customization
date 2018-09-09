# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
from frappe.utils import date_diff


status_map = {
    'Submitted': 'Active',
    'Stopped': 'Stopped',
    'Cancelled': 'Cancelled',
    'Completed': 'Stopped',
}


class GymMembership(Document):
    def onload(self):
        self.set_onload('current_outstanding', 100)

    def update_expiry_date(self, expiry_date, force=False):
        if force or date_diff(expiry_date, self.expiry_date) > 0:
            self.expiry_date = expiry_date
            self.save()
