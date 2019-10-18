# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


def execute():
    for row in _get_names():
        frappe.db.set_value(
            "Sales Invoice",
            row.get("name"),
            "gym_member_name",
            row.get("gym_member_name"),
        )


def _get_names():
    return frappe.db.sql(
        """
            SELECT
                si.name AS name,
                gm.member_name AS gym_member_name
            FROM `tabSales Invoice` AS si
            LEFT JOIN `tabGym Member` AS gm ON
                gm.name = si.gym_member
            WHERE
                IFNULL(si.gym_member, '') != '' AND IFNULL(si.gym_member_name, '') = ''
        """,
        as_dict=1,
    )
