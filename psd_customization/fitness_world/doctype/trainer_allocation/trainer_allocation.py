# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, add_days, date_diff, getdate
from frappe.model.document import Document


class TrainerAllocation(Document):
    def validate(self):
        if getdate(self.to_date) < getdate(self.from_date):
            frappe.throw(
                'From Date cannot be after To Date.'
            )
        sub_from_date, sub_to_date = frappe.db.get_value(
            'Gym Subscription',
            self.gym_subscription,
            ['from_date', 'to_date']
        )
        if getdate(self.from_date) < getdate(sub_from_date) \
                or getdate(self.to_date) > getdate(sub_to_date):
            frappe.throw(
                'Date out of bounds of Subscription period.'
            )
        existing = frappe.db.sql(
            """
                SELECT 1 FROM `tabTrainer Allocation`
                WHERE
                    name!=%(name)s AND
                    gym_subscription=%(gym_subscription)s AND
                    from_date<=%(to_date)s AND
                    to_date>=%(from_date)s
            """,
            values={
                'name': self.name,
                'gym_subscription': self.gym_subscription,
                'from_date': self.from_date,
                'to_date': self.to_date,
            },
        )
        if existing:
            frappe.throw(
                'Another allocation already exists during this time frame.'
            )

    def before_save(self):
        self.gym_member, sub_item, day_fraction = frappe.db.get_value(
            'Gym Subscription',
            self.gym_subscription,
            ['member', 'subscription_item', 'day_fraction'],
        )
        trainer_cost = frappe.db.get_value(
            'Gym Subscription Item', sub_item, 'base_trainer_cost',
        )
        days = date_diff(
            add_days(self.to_date, 1),
            self.from_date
        )
        self.cost = trainer_cost * day_fraction * flt(days)
        self.gym_trainer_name = frappe.db.get_value(
            'Gym Trainer', self.gym_trainer, 'trainer_name',
        )
