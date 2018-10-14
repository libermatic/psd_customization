# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

from psd_customization.fitness_world.api.gym_membership \
    import get_membership_by


class GymMembership(Document):
    def validate(self):
        if self.type == 'Repeating' and not self.end_date:
            frappe.throw('End Date cannot be empty for Repeating Memberships')
        existing = get_membership_by(
            self.member, self.start_date, self.end_date
        )
        if existing:
            frappe.throw(
                'Another active Membership {0} already exists for this Member.'
                ' If you want to create a new Membership, please stop the'
                ' previous one.'
                .format(existing.name)
            )
