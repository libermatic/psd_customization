# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


def execute():
    frappe.get_doc({
        "doctype": "Stock Entry Type",
        "name": "Material Transfer for Expiry",
        "purpose": "Material Transfer",
    }).insert(ignore_if_duplicate=True)