# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from toolz import compose


def execute(filters=None):
    conditions = make_conditions(filters)
    return get_columns(), map(
        compose(make_row, inject_cols),
        query_data(conditions)
    )


def get_columns():
    columns = [
        _('Member ID') + ':Link/Gym Member:120',
        _('Member Name') + '::180',
        _('Activity') + '::90',
        _('Item Code') + '::90',
        _('Subscription Item Name') + '::150',
        _('Expires On') + ':Date:90',
        _('Expiry (In Days)') + ':Int:90',
        _('Ref Subscription') + ':Link/Gym Subscription:120',
        _('Status') + '::90',
    ]
    return columns


def make_conditions(filters={}):
    conds = []
    if filters.get('member'):
        conds.append(
            "m.name = '{}'".format(filters.get('member'))
        )
    if filters.get('member_status'):
        conds.append(
            "m.status = '{}'".format(filters.get('member_status'))
        )
    if filters.get('subscription_item'):
        conds.append(
            "mi.item_code = '{}'".format(filters.get('subscription_item'))
        )
    if filters.get('subscription_status'):
        conds.append(
            "ms.status = '{}'".format(filters.get('subscription_status'))
        )
    return conds


def query_data(conditions):
    return frappe.db.sql(
        """
            SELECT
                m.name AS member_id,
                m.member_name AS member_name,
                m.status AS member_status,
                mi.item_code AS item_code,
                mi.item_name AS item_name,
                MAX(mi.end_date) AS expiry_date,
                ms.name AS subscription,
                ms.status AS subscription_status
            FROM
                `tabGym Member` AS m,
                `tabGym Subscription` AS ms,
                `tabGym Subscription Item` AS mi
            WHERE
                %s
                m.name = ms.member AND
                ms.name = mi.parent
            GROUP BY m.name, mi.item_code
        """ % (
            ' AND '.join(conditions) + ' AND ' if conditions else '',
        ),
        as_dict=1,
    )


def inject_cols(row):
    row_dict = frappe._dict(row)
    if row_dict.expiry_date:
        row_dict.expiry_status = (
            row_dict.expiry_date - frappe.utils.datetime.date.today()
        ).days
    return row_dict


def make_row(row):
    keys = [
        'member_id', 'member_name', 'member_status',
        'item_code', 'item_name', 'expiry_date', 'expiry_status',
        'subscription', 'subscription_status',
    ]
    return map(lambda x: row.get(x), keys)
