# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, date_diff, formatdate, cint
from frappe.model.document import Document
from functools import reduce, partial
from toolz import compose

from psd_customization.fitness_world.api.gym_membership import (
    get_items, dispatch_sms
)


class GymMembership(Document):
    def onload(self):
        if self.reference_invoice and self.docstatus == 1:
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
        def pick_date(key):
            return compose(
                partial(map, lambda x: getdate(x)),
                partial(filter, lambda x: x),
                partial(map, lambda x: x.get(key)),
                partial(map, lambda x: x.as_dict()),
            )
        if not self.items:
            map(
                lambda item: self.append('items', item),
                get_items(self.membership, self.duration),
            )
        self.from_date = compose(min, pick_date('start_date'))(self.items)
        self.to_date = compose(max, pick_date('end_date'))(self.items)
        self.validate_dates()
        self.total_amount = reduce(lambda a, x: a + x.amount, self.items, 0)

    def before_submit(self):
        self.status = 'Unpaid'

    def on_submit(self):
        if not cint(self.no_invoice):
            self.reference_invoice = self.create_sales_invoice()

    def on_update_after_submit(self):
        if self.status == 'Paid':
            dispatch_sms(self.name, 'sms_receipt')

    def on_cancel(self):
        if self.reference_invoice:
            si = frappe.get_doc('Sales Invoice', self.reference_invoice)
            if si.docstatus == 1:
                si.cancel()

    def validate_dates(self):
        enrollment_date = frappe.db.get_value(
            'Gym Member', self.member, 'enrollment_date'
        )
        if date_diff(self.from_date, enrollment_date) < 0:
            return frappe.throw(
                'Membership cannot start before enrollment date {}.'.format(
                    formatdate(enrollment_date)
                )
            )
        for item in filter(lambda x: not cint(x.one_time), self.items):
            if frappe.db.sql(
                """
                    SELECT EXISTS(
                        SELECT 1 FROM
                            `tabGym Membership Item` AS mi,
                            `tabGym Membership` as ms
                        WHERE
                            mi.item_code = '{item_code}' AND
                            mi.parent = ms.name AND
                            ms.docstatus = 1 AND
                            ms.member = '{member}' AND
                            mi.start_date <= '{end_date}' AND
                            mi.end_date >= '{start_date}'
                    )
                """.format(
                    member=self.member,
                    item_code=item.item_code,
                    start_date=item.start_date,
                    end_date=item.end_date,
                ),
            )[0][0]:
                return frappe.throw(
                    'Another Membership for {item_code} already exists during'
                    ' this time frame.'.format(item_code=item.item_name)
                )

    def create_sales_invoice(self):
        si = frappe.new_doc('Sales Invoice')
        si.set_posting_time = 1
        si.posting_date = self.posting_date
        si.customer = frappe.db.get_value(
            'Gym Member', self.member, 'customer'
        )

        def get_description(item):
            if not item.start_date:
                return item.item_name
            return '{item_name}: Valid from {start_date} to {end_date}'.format(
                item_name=item.item_name,
                start_date=item.get_formatted('start_date'),
                end_date=item.get_formatted('end_date'),
            )
        for item in self.items:
            si.append('items', {
                'item_code': item.item_code,
                'description': get_description(item),
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
