# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from functools import partial
from toolz import compose, pluck

from psd_customization.utils.report import make_column


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
    return [
        make_column("sales_invoice", type="Link", options="Sales Invoice"),
        make_column("posting_date", "Date", type="Date", width=90),
        make_column("customer", type="Link", options="Customer"),
        make_column("customer_name", width=150),
        make_column("item_code", type="Link", options="Item"),
        make_column("qty", type="Float", width=90),
        make_column("delivered_qty", type="Float", width=90),
        make_column("pending_qty", type="Float", width=90),
        make_column("item_name", width=150),
        make_column("amount", type="Currency"),
    ]


def _get_filters(filters):
    clauses = [
        "si.docstatus = 1",
        "si.update_stock = 0",
        "i.is_stock_item = 1",
        "sii.delivered_qty < sii.stock_qty",
    ]
    return " AND ".join(clauses), filters


def _get_data(clauses, keys, values):
    items = frappe.db.sql(
        """
            SELECT
                si.name AS sales_invoice,
                si.posting_date AS posting_date,
                si.customer AS customer,
                si.customer_name AS customer_name,
                sii.item_code AS item_code,
                sii.item_name AS item_name,
                sii.stock_qty AS qty,
                sii.delivered_qty AS delivered_qty,
                (sii.stock_qty - sii.delivered_qty) AS pending_qty,
                sii.amount AS amount
            FROM `tabSales Invoice Item` AS sii
            LEFT JOIN `tabSales Invoice` AS si ON si.name = sii.parent
            LEFT JOIN `tabItem` AS i ON i.name = sii.item_code
            WHERE {clauses}
            ORDER BY si.posting_date
        """.format(
            clauses=clauses
        ),
        as_dict=1,
    )
    return items
