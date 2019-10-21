# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate
from frappe.model.document import Document


class TrainerAllocation(Document):
    def validate(self):
        self.validate_subscription()
        self.validate_dates()
        self.validate_existing()

    def validate_subscription(self):
        subscription = frappe.get_doc("Gym Subscription", self.gym_subscription)
        if not subscription or subscription.docstatus != 1:
            frappe.throw("Invalid Subscription: {}".format(self.gym_subscription))

    def validate_dates(self):
        if getdate(self.to_date) < getdate(self.from_date):
            frappe.throw("From Date cannot be after To Date.")
        sub_from_date, sub_to_date = frappe.db.get_value(
            "Gym Subscription", self.gym_subscription, ["from_date", "to_date"]
        )
        if getdate(self.from_date) < getdate(sub_from_date) or getdate(
            self.to_date
        ) > getdate(sub_to_date):
            frappe.throw("Date out of bounds of Subscription period.")
        if self.salary_till and not (
            getdate(self.from_date)
            <= getdate(self.salary_till)
            <= getdate(self.to_date)
        ):
            frappe.throw("Payroll Date out of bounds of Trainer Allocation period.")

    def validate_existing(self):
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
                "name": self.name,
                "gym_subscription": self.gym_subscription,
                "from_date": self.from_date,
                "to_date": self.to_date,
            },
        )
        if existing:
            frappe.throw("Another allocation already exists during this time frame.")

    def before_save(self):
        self.gym_member, self.gym_member_name = frappe.db.get_value(
            "Gym Subscription", self.gym_subscription, ["member", "member_name"]
        )
        self.gym_trainer_name = frappe.db.get_value(
            "Gym Trainer", self.gym_trainer, "trainer_name"
        )
