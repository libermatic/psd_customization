# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


def _get_user_companies(user):
    return set(
        frappe.get_all(
            "User Permission",
            filters={"allow": "Company", "user": user},
            pluck="for_value",
        )
    )


def set_user_defaults(login_manager):
    if frappe.session.user:
        company = frappe.defaults.get_user_default('company')
        allowed_companies = _get_user_companies(frappe.session.user)
        if allowed_companies and company not in allowed_companies:
            frappe.defaults.add_user_default(
                'company',
                company,
                parenttype='User Permission',
            )
