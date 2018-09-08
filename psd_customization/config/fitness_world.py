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
                    "name": "Gym Fee",
                    "label": "Fee",
                },
            ]
        },
        {
            "label": _("Setup"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Gym SMS Template",
                    "label": "SMS Template",
                },
                {
                    "type": "doctype",
                    "name": "Gym Settings",
                    "label": "Gym Settings",
                },
            ]
        },
    ]
