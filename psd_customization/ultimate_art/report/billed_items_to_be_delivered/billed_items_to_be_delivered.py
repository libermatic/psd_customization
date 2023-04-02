# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

import frappe

from psd_customization.utils.report import make_column


def execute(filters=None):
    columns = _get_columns(filters)
    data = _get_data(filters)
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


def _get_data(filters):
    SalesInvoiceItem = frappe.qb.DocType("Sales Invoice Item")
    SalesInvoice = frappe.qb.DocType("Sales Invoice")
    Item = frappe.qb.DocType("Item")
    return (
        frappe.qb.from_(SalesInvoiceItem)
        .left_join(SalesInvoice)
        .on(SalesInvoice.name == SalesInvoiceItem.parent)
        .left_join(Item)
        .on(Item.name == SalesInvoiceItem.item_code)
        .select(
            SalesInvoice.name.as_("sales_invoice"),
            SalesInvoice.posting_date,
            SalesInvoice.customer,
            SalesInvoice.customer_name,
            SalesInvoiceItem.item_code,
            SalesInvoiceItem.item_name,
            SalesInvoiceItem.stock_qty,
            SalesInvoiceItem.delivered_qty,
            (SalesInvoiceItem.stock_qty - SalesInvoiceItem.delivered_qty).as_(
                "pending_qty"
            ),
            SalesInvoiceItem.amount,
        )
        .where(
            (SalesInvoice.docstatus == 1)
            & (SalesInvoice.update_stock == 0)
            & (Item.is_stock_item == 1)
            & (SalesInvoiceItem.delivered_qty < SalesInvoiceItem.stock_qty)
        )
        .orderby(SalesInvoice.posting_date)
    ).run(as_dict=True)
