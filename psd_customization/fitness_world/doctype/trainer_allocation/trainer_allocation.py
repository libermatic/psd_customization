# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class TrainerAllocation(Document):
    def before_save(self):
        self.gym_member = frappe.db.get_valye(
            'Gym Subscription', self.gym_subscription, 'member'
        )
