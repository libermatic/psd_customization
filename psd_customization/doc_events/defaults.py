# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from toolz import pluck, first


def _get_user_companies(user):
    result = frappe.db.sql(
        """
            SELECT for_value FROM `tabUser Permission`
            WHERE allow='Company' AND user=%(user)s
        """,
        values={'user': user},
        as_dict=1,
    )
    return list(pluck('for_value', result))


def set_user_defaults(login_manager):
    if frappe.session.user:
        company = frappe.defaults.get_user_default('company')
        allowed_companies = _get_user_companies(frappe.session.user)
        if allowed_companies and company not in allowed_companies:
            frappe.defaults.add_user_default(
                'company',
                first(allowed_companies),
                parenttype='User Permission',
            )
