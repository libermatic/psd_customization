# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from toolz.curried import merge, keyfilter

from psd_customization.ultimate_art.api.label_printer import get_item_details


class LabelPrinter(Document):
    @frappe.whitelist()
    def set_items_from_reference(self):
        ref_doc = frappe.get_doc(self.print_dt, self.print_dn)
        self.items = []
        for ref_item in ref_doc.items:
            self.append(
                "items",
                merge(
                    keyfilter(
                        lambda x: x in ["item_code", "item_name", "qty", "batch_no"],
                        ref_item.as_dict(),
                    ),
                    get_item_details(
                        ref_item.item_code,
                        ref_item.batch_no,
                        price_list=self.price_list,
                    ),
                ),
            )
