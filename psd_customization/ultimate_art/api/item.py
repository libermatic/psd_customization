# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import fmt_money
from toolz import merge

from psd_customization.utils.fp import mapr


@frappe.whitelist()
def get_label_data(item_code, company=None, price_list=None):
    item = frappe.get_doc("Item", item_code)
    if not item:
        return None
    settings = frappe.get_single("Retail Settings")
    price = _get_price(
        item.item_code, price_list or settings.barcode_price_list, item.variant_of
    )
    return mapr(
        lambda x: merge(
            {
                "company": company or settings.barcode_company,
                "item_code": item.item_code,
                "item_name": item.item_name,
                "barcode": x.barcode,
                "type": x.barcode_type,
            },
            _make_price(price),
        ),
        item.barcodes,
    )


def _get_price(item_code, price_list, template_item_code=None):
    price = frappe.get_all(
        "Item Price",
        fields=["price_list_rate", "currency"],
        filters={"price_list": price_list, "item_code": item_code},
    )
    if price:
        return price[0]
    if template_item_code:
        price = frappe.get_all(
            "Item Price",
            fields=["price_list_rate", "currency"],
            filters={"price_list": price_list, "item_code": template_item_code},
        )
        if price:
            return price[0]
    return None


def get_price(item_code, price_list):
    return _get_price(item_code, price_list)


def _make_price(price):
    if not price:
        return {}
    return {
        "price": price.price_list_rate,
        "currency": price.currency,
        "price_formatted": fmt_money(price.price_list_rate, currency=price.currency),
    }
