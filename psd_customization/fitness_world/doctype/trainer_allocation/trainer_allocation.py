# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class TrainerAllocation(Document):
    def validate(self):
        existing = frappe.db.sql(
            """
                SELECT 1 FROM `tabTrainer Allocation`
                WHERE
                    gym_subscription=%(gym_subscription)s AND
                    from_date<=%(to_date)s AND
                    to_date>=%(from_date)s
            """,
            values={
                'gym_subscription': self.gym_subscription,
                'from_date': self.from_date,
                'to_date': self.to_date,
            },
            debug=1,
        )
        if existing:
            frappe.throw(
                'Another allocation already exists during this time frame.'
            )

    def before_save(self):
        self.gym_member = frappe.db.get_value(
            'Gym Subscription', self.gym_subscription, 'member',
        )
        self.gym_trainer_name = frappe.db.get_value(
            'Gym Trainer', self.gym_trainer, 'trainer_name',
        )
