# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "label": _("Gym"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Gym Member",
                    "label": "Member",
                },
                {
                    "type": "doctype",
                    "name": "Gym Membership",
                    "label": "Membership",
                },
                {
                    "type": "doctype",
                    "name": "Gym Subscription",
                    "label": "Subscription",
                },
            ]
        },
        {
            "label": _("Setup"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Gym Subscription Plan",
                    "label": "Subscription Plan",
                },
                {
                    "type": "doctype",
                    "name": "SMS Template",
                    "label": "SMS Template",
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
