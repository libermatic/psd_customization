# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, date_diff, formatdate
from frappe.model.document import Document
from functools import reduce

from psd_customization.fitness_world.api.gym_membership import (
    get_next_from_date, get_to_date, get_items, dispatch_sms
)


class GymMembership(Document):
    def onload(self):
        if self.docstatus == 1:
            rounded_total, status = frappe.db.get_value(
                'Sales Invoice',
                self.reference_invoice,
                ['rounded_total', 'status'],
            )
            self.set_onload('si_value', rounded_total)
            self.set_onload('si_status', status)

    def validate(self):
        if not self.items:
            frappe.throw('Services cannot be empty.')

    def before_save(self):
        if not self.from_date:
            self.from_date = get_next_from_date(self.member)
        if not self.items:
            map(
                lambda item: self.append('items', item),
                get_items(self.membership, self.duration),
            )
        frequency = frappe.db.get_value(
            'Gym Membership Plan', self.membership_plan, 'frequency'
        )
        self.to_date = get_to_date(self.from_date, frequency)
        self.validate_dates()
        self.total_amount = reduce(lambda a, x: a + x.amount, self.items, 0)

    def before_submit(self):
        self.status = 'Unpaid'

    def on_submit(self):
        self.reference_invoice = self.create_sales_invoice()
        self.save()

    def on_update_after_submit(self):
        member = frappe.get_doc('Gym Member', self.member)
        member.update_expiry_date()
        if self.status == 'Paid':
            dispatch_sms(self.name, 'sms_receipt')

    def on_cancel(self):
        si = frappe.get_doc('Sales Invoice', self.reference_invoice)
        si.cancel()

    def validate_dates(self):
        existing_membership = frappe.db.sql(
            """
                SELECT name FROM `tabGym Membership`
                WHERE docstatus = 1 AND
                    member = '{member}' AND (
                    '{from_date}' BETWEEN from_date AND to_date
                    OR '{to_date}' BETWEEN from_date AND to_date
                )
            """.format(
                member=self.member,
                from_date=self.from_date,
                to_date=self.to_date
            )
        )
        print(existing_membership)
        if existing_membership:
            return frappe.throw(
                'Another membership already exists during this time frame. '
                'Please refresh to let the system auto-set the dates.'
            )
        enrollment_date = frappe.db.get_value(
            'Gym Member', self.member, 'enrollment_date'
        )
        if date_diff(self.from_date, enrollment_date) < 0:
            return frappe.throw(
                'Membership cannot start before enrollment date {}.'.format(
                    formatdate(enrollment_date)
                )
            )

    def create_sales_invoice(self):
        si = frappe.new_doc('Sales Invoice')
        si.set_posting_time = 1
        si.posting_date = self.posting_date
        si.customer = frappe.db.get_value(
            'Gym Member', self.member, 'customer'
        )
        for item in self.items:
            si.append('items', {
                'item_code': item.item_code,
                'qty': item.qty,
                'rate': item.rate,
            })
        settings = frappe.get_single('Gym Settings')
        si.company = settings.default_company
        si.cost_center = frappe.db.get_value(
            'Company', settings.default_company, 'cost_center',
        )
        si.naming_series = settings.naming_series
        si.taxes_and_charges = settings.default_tax_template
        si.set_taxes()
        si.append('payment_schedule', {
            'due_date': max(
                getdate(self.to_date), getdate(self.posting_date)
            ),
            'invoice_portion': 100,
        })
        si.save()
        si.submit()
        return si.name
