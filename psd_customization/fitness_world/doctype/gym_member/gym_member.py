# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.contacts.address_and_contact import (
    load_address_and_contact,
    delete_contact_and_address,
)
import operator
from functools import reduce, partial
from toolz import count, pluck, compose, first, excepts

from psd_customization.utils.fp import pick
from psd_customization.fitness_world.api.gym_subscription import get_currents
from psd_customization.fitness_world.api.trainer_allocation import get_last


def _get_trainer(member, subscriptions):
    training_sub = compose(
        excepts(StopIteration, first, lambda __: None),
        partial(filter, lambda x: x.get("is_training") == 1),
    )(subscriptions)
    if not training_sub:
        return None
    return get_last(member, subscription_item=training_sub.get("item"))


class GymMember(Document):
    def onload(self):
        load_address_and_contact(self)
        self.load_subscription_details()

    def autoname(self):
        if not self.member_id:
            key = frappe.get_meta(self.doctype).autoname or ""
            self.member_id = make_autoname(key)
        self.name = self.member_id

    def validate(self):
        self.validate_member_id()
        if not self.enrollment_date:
            frappe.throw("Enrollment Date cannot be empty.")

    def validate_member_id(self):
        key = frappe.get_meta(self.doctype).autoname or ""
        error_message = (
            "Member ID should follow this pattern: "
            "<strong>{}</strong>".format(key.replace(".", ""))
        )
        if len(key.replace(".", "")) != len(self.member_id):
            frappe.throw(error_message)
        rules = ["YY", "YYYY", "MM", "DD", "FY"]
        get_parts = compose(
            partial(filter, lambda x: not x.startswith("#")),
            partial(filter, lambda x: x not in rules),
            lambda x: x.split("."),
        )
        for part in get_parts(key):
            if part not in self.member_id:
                frappe.throw(error_message)

    def before_save(self):
        self.flags.is_new_doc = self.is_new()
        if not self.customer:
            self.customer = self.create_customer()
        if not self.notification_contact:
            self.notification_number = None

    def on_update(self):
        if self.flags.is_new_doc:
            self.make_contact_and_address(
                pick(
                    [
                        "email_id",
                        "mobile_no",
                        "address_line1",
                        "address_line2",
                        "city",
                        "state",
                        "pincode",
                        "country",
                    ],
                    self,
                )
            )

    def on_trash(self):
        # clears notification_contact for LinkExistsException
        self.db_set("notification_contact", None)
        self.db_set("emergency_contact", None)
        delete_contact_and_address("Gym Member", self.name)

    def after_delete(self):
        frappe.delete_doc("Customer", self.customer)

    def load_subscription_details(self):
        all_subscriptions = frappe.db.sql(
            """
                SELECT
                    si.outstanding_amount AS amount,
                    si.status AS status,
                    gs.to_date AS end_date
                FROM `tabGym Subscription` AS gs, `tabSales Invoice` AS si
                WHERE
                    gs.docstatus = 1 AND
                    gs.member = '{member}' AND
                    gs.reference_invoice = si.name
                ORDER BY gs.from_date DESC
            """.format(
                member=self.name
            ),
            as_dict=True,
        )
        unpaid_subscriptions = filter(
            lambda x: x.get("status") != "Paid", all_subscriptions
        )
        outstanding = reduce(operator.add, pluck("amount", unpaid_subscriptions), 0)

        self.set_onload(
            "subscription_details",
            {
                "total_invoices": count(all_subscriptions),
                "unpaid_invoices": count(unpaid_subscriptions),
                "outstanding": outstanding,
            },
        )
        subscriptions = get_currents(self.name)
        self.set_onload("subscriptions", subscriptions)
        self.set_onload("last_trainer", _get_trainer(self.name, subscriptions))

    def fetch_and_link_doc(self, doctype, fetch_fn):
        docname = fetch_fn("Customer", self.customer)
        if docname:
            doc = frappe.get_doc(doctype, docname)
            doc.append("links", {"link_doctype": "Gym Member", "link_name": self.name})
            doc.save()
        return docname

    def make_contact_and_address(self, args, is_primary_contact=1):
        if any(field in args.keys() for field in ["email_id", "mobile_no"]):
            contact = frappe.get_doc(
                {
                    "doctype": "Contact",
                    "first_name": self.member_name,
                    "email_id": args.get("email_id"),
                    "mobile_no": args.get("mobile_no"),
                    "is_primary_contact": is_primary_contact,
                    "links": [{"link_doctype": "Gym Member", "link_name": self.name}],
                }
            ).insert()
            # sets notification_contact and number
            self.db_set("notification_contact", contact.name)
            self.db_set("notification_number", contact.mobile_no)
        if all(field in args.keys() for field in ["address_line1", "city"]):
            frappe.get_doc(
                {
                    "doctype": "Address",
                    "address_title": self.member_name,
                    "address_type": "Personal",
                    "address_line1": args.get("address_line1"),
                    "address_line2": args.get("address_line2"),
                    "city": args.get("city"),
                    "state": args.get("state"),
                    "pincode": args.get("pincode"),
                    "country": args.get("country"),
                    "links": [{"link_doctype": "Gym Member", "link_name": self.name}],
                }
            ).insert()
        print("done")

    def create_customer(self):
        customer_group = frappe.get_value(
            "Gym Settings", None, "default_customer_group"
        )
        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": self.member_name,
                "customer_type": "Individual",
                "customer_group": customer_group or "All Customer Groups",
                "territory": "All Territories",
            }
        ).insert()
        return customer.name
