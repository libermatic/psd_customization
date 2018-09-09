# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate
from functools import reduce
from frappe.model.document import Document

from psd_customization.fitness_world.api.gym_fee import (
    get_next_from_date, get_to_date, get_items
)


class GymFee(Document):
    def before_save(self):
        if not self.from_date:
            self.from_date = get_next_from_date(self.membership)
        if not self.duration:
            self.duration = 1
        if not self.to_date:
            self.to_date = get_to_date(
                self.membership, self.from_date, self.duration
            )
        if not self.items:
            map(
                lambda item: self.append('items', item),
                get_items(self.membership, self.duration),
            )
        self.total_amount = reduce(lambda a, x: a + x.amount, self.items, 0)

    def before_submit(self):
        self.status = 'Unpaid'

    def on_submit(self):
        self.reference_invoice = self.create_sales_invoice()
        self.save()

    def on_cancel(self):
        if self.flags.prev_si:
            si = frappe.get_doc('Sales Invoice', self.flags.prev_si)
            si.cancel()

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
        si.taxes_and_charges = frappe.db.get_value(
            'Gym Settings', None, 'default_tax_template',
        )
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
