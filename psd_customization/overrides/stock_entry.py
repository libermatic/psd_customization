import frappe
from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry as Standard


class StockEntry(Standard):
    def validate_serialized_batch(self):
        from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

        if self.stock_entry_type == "Material Transfer for Expiry":
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
                                frappe._(
                                    "Row #{0}: Serial No {1} does not belong to Batch {2}"
                                ).format(d.idx, row.name, d.batch_no)
                            )
            return
        
        return super().validate_serialized_batch()
