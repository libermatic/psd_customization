# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

import frappe
from erpnext.stock.get_item_details import get_item_price
from toolz import merge


@frappe.whitelist()
def get_item_details(item_code, batch_no=None, price_list=None):
    return merge(
        {"price": _get_price(item_code, batch_no, price_list)},
        _get_batch(batch_no),
        _get_barcode(item_code),
    )


def _get_price(item_code, batch_no, price_list):
    args = {
        "price_list": price_list
        or frappe.get_cached_value("Selling Settings", None, "selling_price_list"),
        "uom": frappe.get_cached_value("Item", item_code, "stock_uom"),
        "transaction_date": frappe.utils.today(),
        "batch_no": batch_no,
    }
    try:
        item_price = get_item_price(args, item_code, ignore_party=True)
        if item_price:
            return item_price[0][1]
        variant_of = frappe.get_cached_value("Item", item_code, "variant_of")
        if variant_of:
            return get_item_price(args, variant_of, ignore_party=True)[0][1]
    except IndexError:
        return None

def _get_batch(batch_no):
    if not batch_no:
        return {}

    try:
        return frappe.get_cached_value(
            "Batch",
            batch_no,
            fieldname=["manufacturing_date", "expiry_date"],
            as_dict=1,
        )
    except frappe.DoesNotExistError:
        return {}


def _get_barcode(item_code):
    try:
        return frappe.get_cached_value(
            "Item Barcode",
            {"parent": item_code},
            fieldname=["barcode", "barcode_type"],
            as_dict=1,
        )
    except frappe.DoesNotExistError:
        return {}