# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, get_link_to_form
from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry

def validate_serialized_batch(self):
    from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

    for d in self.get("items"):
        if (
            hasattr(d, "serial_no")
            and hasattr(d, "batch_no")
            and d.serial_no
            and d.batch_no
        ):
            serial_nos = frappe.get_all(
                "Serial No",
                fields=["batch_no", "name", "warehouse"],
                filters={"name": ("in", get_serial_nos(d.serial_no))},
            )

            for row in serial_nos:
                if row.warehouse and row.batch_no != d.batch_no:
                    frappe.throw(
                        _(
                            "Row #{0}: Serial No {1} does not belong to Batch {2}"
                        ).format(d.idx, row.name, d.batch_no)
                    )

        if (
            self.stock_entry_type != "Material Transfer for Expiry"
            and flt(d.qty) > 0.0
            and d.get("batch_no")
            and self.get("posting_date")
            and self.docstatus < 2
        ):
            expiry_date = frappe.get_cached_value(
                "Batch", d.get("batch_no"), "expiry_date"
            )

            if expiry_date and getdate(expiry_date) < getdate(self.posting_date):
                frappe.throw(
                    _("Row #{0}: The batch {1} has already expired.").format(
                        d.idx, get_link_to_form("Batch", d.get("batch_no"))
                    )
                )


def before_validate(doc, method):
    StockEntry.validate_serialized_batch = validate_serialized_batch