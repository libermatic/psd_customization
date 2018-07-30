# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters={}):
    data = query_stock_entry_ledger(filters)
    return get_columns(), map(make_row, data)


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
        _('Valuation Rate') + ':Currency/currency:90',
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
            ORDER BY sle.item_code
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


def make_row(row):
    row_dict = frappe._dict(row)
    keys = [
        'item_code', 'item_name', 'warehouse',
        'batch_no', 'expiry_date', 'expiry_status',
        'qty', 'rate', 'valuation_rate'
    ]
    if row_dict.expiry_date:
        row_dict.expiry_status = (
            row.expiry_date - frappe.utils.datetime.date.today()
        ).days
    return map(lambda x: row_dict.get(x), keys)
