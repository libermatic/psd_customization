# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, getdate
from frappe.model.document import Document

from psd_customization.fitness_world.api.gym_subscription import validate_dependencies


class GymSubscription(Document):
    def onload(self):
        if self.reference_invoice:
            rounded_total, status = frappe.db.get_value(
                "Sales Invoice", self.reference_invoice, ["rounded_total", "status"]
            )
            self.set_onload("invoice", {"amount": rounded_total, "status": status})

    def validate(self):
        self.validate_dates()
        self.validate_item()
        if self.flags.source_doc != "Sales Invoice":
            validate_dependencies(
                self.member,
                [
                    frappe._dict(
                        {
                            "item_code": self.subscription_item,
                            "item_name": self.subscription_name,
                            "from_date": self.from_date,
                            "to_date": self.to_date,
                            "is_lifetime": self.is_lifetime,
                        }
                    )
                ],
            )
        self.validate_opening()

    def validate_dates(self):
        if not cint(self.is_lifetime):
            if not self.from_date or not self.to_date:
                frappe.throw("Both dates are required")
            if getdate(self.from_date) > getdate(self.to_date):
                frappe.throw("From date cannot be after to date")
        if not self.from_date:
            frappe.throw("Start Date cannot be empty")

    def validate_item(self):
        if cint(self.is_lifetime):
            can_be_lifetime = frappe.db.get_value(
                "Gym Subscription Item", self.subscription_item, "can_be_lifetime"
            )
            if not cint(can_be_lifetime):
                return frappe.throw(
                    "Subscription Item {} cannot be Lifetime".format(
                        self.subscription_name
                    )
                )

    def validate_opening(self):
        if cint(self.is_opening) and self.reference_invoice:
            return frappe.throw(
                "Opening Subscription cannot be linked to a Sales Invoice."
            )

    def before_save(self):
        if cint(self.is_lifetime):
            self.to_date = None
        if (
            self.flags.source_doc != "Sales Invoice"
            and self.is_new()
            and self.reference_invoice
        ):
            self.reference_invoice = None

    def before_submit(self):
        needs_trainer = frappe.db.get_value(
            "Gym Subscription Item", self.subscription_item, "requires_trainer"
        )
        self.status = "Active"
        if cint(needs_trainer):
            self.is_training = 1

    def before_update_after_submit(self):
        self.validate_opening()

    def before_cancel(self):
        if self.reference_invoice:
            row_item_name = frappe.db.exists(
                "Sales Invoice Item",
                {"parent": self.reference_invoice, "gym_subscription": self.name},
            )
            if row_item_name:
                frappe.db.set_value(
                    "Sales Invoice Item", row_item_name, "gym_subscription", None
                )
