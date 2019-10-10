# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import compose, pluck


def execute():
    frappe.db.set_value(
        "Stock Settings",
        "Stock Settings",
        {
            "use_naming_series": 1,
            "naming_series_prefix": "{{ frappe.utils.getdate(expiry_date).strftime('%m%y') if expiry_date else '0000' }}/{{ item }}/",  # noqa
        },
    )
    for name in _get_names("Item", filters={"has_batch_no": 1, "has_expiry_date": 1}):
        frappe.db.set_value("Item", name, "create_new_batch", 1)


_get_names = compose(partial(pluck, "name"), frappe.get_all)
