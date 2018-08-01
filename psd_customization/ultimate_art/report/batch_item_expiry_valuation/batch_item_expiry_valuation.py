# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint
from functools import partial
from psd_customization.utils.fp import compose


def execute(filters={}):
    data = query_stock_entry_ledger(filters)
    filter_post_query = filter_data(filters)
    post_proced = map(inject_cols, data)
    return get_columns(), map(make_row, filter_post_query(post_proced))


def get_columns():
    columns = [
        _('Item') + ':Link/Item:90',
        _('Item Name') + '::120',
        _('Warehouse') + ':Link/Warehouse:90',
        _('Batch') + ':Link/Batch:120',
        _('Expires On') + ':Date:90',
        _('Expiry (In Days)') + ':Int:90',
        _('Quantity') + ':Float:90',
        _('Item Rate') + ':Currency/currency:90',
        _('Amount') + ':Currency/currency:90',
        _('Valuation Rate') + ':Currency/currency:90',
        _('Total Valuation') + ':Currency/currency:90',
    ]
    return columns


def query_stock_entry_ledger(filters):
    sub_query = """
        SELECT valuation_rate
        FROM `tabStock Ledger Entry`
        WHERE item_code = sle.item_code
        ORDER BY posting_date DESC, posting_time DESC, name DESC
        LIMIT 1
    """
    return frappe.db.sql(
        """
            SELECT
                sle.item_code,
                item.item_name,
                sle.warehouse,
                sle.batch_no,
                batch.expiry_date,
                SUM(sle.actual_qty) AS qty,
                price.price_list_rate AS rate,
                (%s) AS valuation_rate
            FROM
                `tabStock Ledger Entry` AS sle,
                `tabBatch` AS batch,
                `tabItem` AS item,
                `tabItem Price` as price
            WHERE sle.docstatus < 2
                AND IFNULL(sle.batch_no, '') != ''
                AND sle.batch_no = batch.name
                AND sle.item_code = item.name
                AND sle.item_code = price.item_code
                AND %s
            GROUP BY sle.batch_no, sle.warehouse
            ORDER BY batch.expiry_date, sle.item_code
        """ % (
            sub_query,
            ' AND '.join(make_conditions(filters)),
        ),
        as_dict=1,
    )


def make_conditions(filters):
    conds = []
    if filters.get('from_date') and filters.get('to_date'):
        conds.append(
            "sle.posting_date BETWEEN '{}' AND '{}'".format(
                filters.get('from_date'), filters.get('to_date')
            )
        )
    else:
        frappe.throw(_('Dates are required'))
    if filters.get('warehouse'):
        conds.append(
            "sle.warehouse = '{}'".format(filters.get('warehouse'))
        )
    conds.append(
        "price.price_list = '{}'".format(
            filters.get('price_list', 'Standard Selling')
        )
    )
    return conds


def filter_data(filters):
    def filter_by_days(x):
        days_to_expiry = filters.get('days_to_expiry')
        if days_to_expiry:
            return x.get('expiry_status') <= cint(days_to_expiry)
        return True

    return compose(
        partial(filter, filter_by_days),
        partial(filter, lambda x: x.get('qty') > 0),
    )


def inject_cols(row):
    row_dict = frappe._dict(row)
    if row_dict.expiry_date:
        row_dict.expiry_status = (
            row.expiry_date - frappe.utils.datetime.date.today()
        ).days
    row_dict.amount = row_dict.qty * row_dict.rate
    row_dict.valuation = row_dict.qty * row_dict.valuation_rate
    return row_dict


def make_row(row):
    keys = [
        'item_code', 'item_name', 'warehouse',
        'batch_no', 'expiry_date', 'expiry_status',
        'qty', 'rate', 'amount', 'valuation_rate', 'valuation',
    ]
    return map(lambda x: row.get(x), keys)
