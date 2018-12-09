# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "label": _("Transations"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Sales Invoice",
                    "label": "Sales Invoice",
                },
                {
                    "type": "doctype",
                    "name": "Gym Subscription",
                    "label": "Subscription",
                },
            ]
        },
        {
            "label": _("Documents"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Gym Member",
                    "label": "Member",
                },
                {
                    "type": "doctype",
                    "name": "Gym Subscription Item",
                    "label": "Subscription Item",
                },
                {
                    "type": "doctype",
                    "name": "Gym Trainer",
                    "label": "Trainer",
                },
            ]
        },
        {
            "label": _("Setup"),
            "items": [
                {
                    "type": "doctype",
                    "name": "SMS Template",
                    "label": "SMS Template",
                },
                {
                    "type": "doctype",
                    "name": "Training Slot",
                    "label": "Training Slot",
                },
                {
                    "type": "doctype",
                    "name": "Gym Settings",
                    "label": "Gym Settings",
                },
            ]
        },
        {
            "label": _("Reports"),
            "items": [
                {
                    "type": "report",
                    "is_query_report": True,
                    "name": "Gym Subscription Status",
                    "label": "Subscription Status",
                },
            ]
        },
    ]
