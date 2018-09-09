# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from toolz import count, first, pluck, get
import operator
from functools import reduce


status_map = {
    'Submitted': 'Active',
    'Stopped': 'Stopped',
    'Cancelled': 'Cancelled',
    'Completed': 'Stopped',
}


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
