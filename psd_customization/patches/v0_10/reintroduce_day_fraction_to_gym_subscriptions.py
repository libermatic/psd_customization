# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from toolz import pluck
from frappe.utils import date_diff, add_days, flt

from psd_customization.utils.datetime import month_diff


def execute():
    subscriptions = frappe.get_all("Gym Subscription", {"is_training": 1})
    for name in pluck("name", subscriptions):
        from_date, to_date = frappe.db.get_value(
            "Gym Subscription", name, ["from_date", "to_date"]
        )
        months = month_diff(from_date, to_date, as_dec=1)
        days = date_diff(add_days(to_date, 1), from_date)
        day_fraction = months / flt(days)
        frappe.db.set_value("Gym Subscription", name, "day_fraction", day_fraction)
