# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class GymSettings(Document):
    def validate(self):
        if self.default_company and self.default_tax_template:
            tax_company = frappe.db.get_value(
                'Sales Taxes and Charges Template',
                self.default_tax_template,
                'company',
            )
            if self.default_company != tax_company:
                frappe.throw(
                    'Incorrect Tax Template selected for {}'.format(
                        self.default_company
                    )
                )
