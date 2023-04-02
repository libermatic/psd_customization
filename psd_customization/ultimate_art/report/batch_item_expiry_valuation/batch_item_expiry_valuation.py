# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder.functions import IfNull, Sum
from frappe import _
from frappe.utils import cint
from functools import partial
from psd_customization.utils.fp import compose


def execute(filters={}):
    data = query_stock_entry_ledger(filters)
    filter_post_query = filter_data(filters)
    post_proced = [inject_cols(x) for x in data]
    return get_columns(), [make_row(x) for x in filter_post_query(post_proced)]


def get_columns():
    columns = [
        _("Item") + ":Link/Item:90",
        _("Item Name") + "::120",
        _("Warehouse") + ":Link/Warehouse:90",
        _("Batch") + ":Link/Batch:120",
        _("Expires On") + ":Date:90",
        _("Expiry (In Days)") + ":Int:90",
        _("Quantity") + ":Float:90",
        _("Item Rate") + ":Currency/currency:90",
        _("Amount") + ":Currency/currency:90",
        _("Valuation Rate") + ":Currency/currency:90",
        _("Total Valuation") + ":Currency/currency:90",
    ]
    return columns


def query_stock_entry_ledger(filters):
    StockLedgerEntry = frappe.qb.DocType("Stock Ledger Entry")
    Batch = frappe.qb.DocType("Batch")
    Item = frappe.qb.DocType("Item")
    ItemPrice = frappe.qb.DocType("Item Price")
    Bin = frappe.qb.DocType("Bin")

    q = (
        frappe.qb.from_(StockLedgerEntry)
        .left_join(Batch)
        .on(Batch.name == StockLedgerEntry.batch_no)
        .left_join(Item)
        .on(Item.name == StockLedgerEntry.item_code)
        .left_join(Bin)
        .on(Bin.item_code == StockLedgerEntry.item_code)
        .where(
            (StockLedgerEntry.docstatus == 1)
            & (IfNull(StockLedgerEntry.batch_no, "") != "")
            & (
                StockLedgerEntry.posting_date[
                    filters.get("from_date") : filters.get("to_date")
                ]
            )
        )
        .select(
            StockLedgerEntry.item_code,
            Item.item_name,
            StockLedgerEntry.warehouse,
            StockLedgerEntry.batch_no,
            Batch.expiry_date,
            Sum(StockLedgerEntry.actual_qty).as_("qty"),
            Bin.valuation_rate,
        )
        .groupby(StockLedgerEntry.batch_no, StockLedgerEntry.warehouse)
        .orderby(Batch.expiry_date)
        .orderby(StockLedgerEntry.item_code)
    )
    if filters.get("warehouse"):
        q = q.where(StockLedgerEntry.warehouse == filters.get("warehouse"))

    entries = q.run(as_dict=True)

    price_list = filters.get("price_list") or "Standard Selling"
    prices = (
        {
            (x.item_code, x.batch_no): x.price_list_rate
            for x in (
                frappe.qb.from_(ItemPrice)
                .select(
                    ItemPrice.item_code,
                    ItemPrice.batch_no,
                    ItemPrice.price_list_rate,
                )
                .where(
                    (ItemPrice.price_list == price_list)
                    & ItemPrice.item_code.isin([x.get("item_code") for x in entries])
                )
                .orderby(ItemPrice.valid_from)
            ).run(as_dict=True)
        }
        if entries
        else {}
    )
    for entry in entries:
        entry.rate = prices.get((entry.item_code, entry.batch_no)) or prices.get(
            (entry.item_code, None)
        )

    return entries


def filter_data(filters):
    def filter_by_days(x):
        days_to_expiry = filters.get("days_to_expiry")
        if days_to_expiry:
            return x.get("expiry_status") is not None and x.get("expiry_status") <= cint(days_to_expiry)
        return True

    return compose(
        list,
        partial(filter, filter_by_days),
        partial(filter, lambda x: x.get("qty") > 0),
    )


def inject_cols(row):
    row_dict = frappe._dict(row)
    if row_dict.expiry_date:
        row_dict.expiry_status = (
            row.expiry_date - frappe.utils.datetime.date.today()
        ).days
    row_dict.amount = row_dict.qty * (row_dict.rate or 0)
    row_dict.valuation = row_dict.qty * row_dict.valuation_rate
    return row_dict


def make_row(row):
    keys = [
        "item_code",
        "item_name",
        "warehouse",
        "batch_no",
        "expiry_date",
        "expiry_status",
        "qty",
        "rate",
        "amount",
        "valuation_rate",
        "valuation",
    ]

    return [row.get(x) for x in keys]
