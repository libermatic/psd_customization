# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from toolz import merge

from psd_customization.ultimate_art.api.item import get_label_data


@frappe.whitelist()
def get_items(print_dt, print_dn, company, price_list):
    doc = frappe.get_doc(print_dt, print_dn) or []
    return map(
        _make_item(company, price_list),
        doc.items,
    )


def _make_item(company, price_list):
    def fn(item):
        return merge(
            get_label_data(item.item_code, company, price_list),
            {'qty': item.qty}
        )
    return fn
