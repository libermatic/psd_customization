# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document


class GymSubscriptionPlan(Document):
    def autoname(self):
        self.name = '{} - {}'.format(self.plan_name, self.frequency)
