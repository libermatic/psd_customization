# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from toolz import count, first, pluck, get
import operator
from functools import reduce


class GymMembership(Document):
    def onload(self):
        all_fees = frappe.db.sql(
            """
                SELECT
                    si.rounded_total AS amount,
                    fee.status AS status,
                    fee.to_date AS end_date
                FROM `tabGym Fee` AS fee, `tabSales Invoice` AS si
                WHERE
                    fee.docstatus = 1 AND
                    fee.membership = '{membership}' AND
                    fee.reference_invoice = si.name
                ORDER BY fee.to_date DESC
            """.format(membership=self.name),
            as_dict=True,
        )
        unpaid_fees = filter(lambda x: x.get('status') == 'Unpaid', all_fees)
        self.set_onload('total_invoices', count(all_fees))
        self.set_onload('unpaid_invoices', count(unpaid_fees))
        outstanding = reduce(operator.add, pluck('amount', unpaid_fees), 0)
        self.set_onload('outstanding', outstanding)
        paid_fees = filter(lambda x: x.get('status') == 'Paid', all_fees)
        end_date = get('end_date', first(paid_fees)) if paid_fees else None
        self.set_onload('end_date', end_date)

    def validate(self):
        if not self.items:
            frappe.throw('Services cannot be empty.')
        existing_memberships = frappe.db.sql(
            """
                SELECT name from `tabGym Membership`
                WHERE docstatus = 1 AND status = 'Active' AND member = '{}'
            """.format(self.member),
            as_dict=1,
        )
        if existing_memberships:
            frappe.throw(
                '{} already has an existing active Membership: {}. You need '
                'to Stop that Membership before creating a new one.'.format(
                    self.member_name,
                    get('name', first(existing_memberships))
                )
            )

    def before_save(self):
        self.total_amount = reduce(lambda a, x: a + x.amount, self.items, 0)

    def before_submit(self):
        self.status = 'Active'
        self.auto_repeat = 'Yes'
