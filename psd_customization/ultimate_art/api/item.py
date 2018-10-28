# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import fmt_money


@frappe.whitelist()
def get_label_data(item_code):
    item = frappe.get_doc('Item', item_code)
    if not item:
        return None
    settings = frappe.get_single('Retail Settings')
    return {
        'company': settings.barcode_company,
        'item_code': item.item_code,
        'item_name': item.item_name,
        'barcode': item.barcode,
        'price_formatted': _get_price(
            item.item_code, settings.barcode_price_list, item.variant_of)
    }


def _get_price(item_code, price_list, template_item_code=None):
    price = frappe.get_all(
        'Item Price',
        fields=['price_list_rate', 'currency'],
        filters={'price_list': price_list, 'item_code': item_code},
    )
    if price:
        return fmt_money(price[0].price_list_rate, currency=price[0].currency)
    if template_item_code:
        price = frappe.get_all(
            'Item Price',
            fields=['price_list_rate', 'currency'],
            filters={
                'price_list': price_list,
                'item_code': template_item_code,
            },
        )
        if price:
            return fmt_money(
                price[0].price_list_rate,
                currency=price[0].currency,
            )
