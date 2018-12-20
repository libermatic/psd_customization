# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document

from psd_customization.ultimate_art.api.item import get_price


class LabelPrinter(Document):
    def before_save(self):
        for item in self.items:
            if not item.price:
                price = get_price(item.item_code, self.price_list) or {}
                item.price = price.get('price_list_rate')
                item.currency = price.get('currency')
