# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from toolz import compose


# TODO: make this work for lifetime subscriptions

def execute(filters=None):
    conditions = make_conditions(filters)
    return get_columns(), map(
        compose(make_row, inject_cols),
        query_data(conditions),
    )


def get_columns():
    columns = [
        _('Member ID') + ':Link/Gym Member:120',
        _('Member Name') + '::180',
        _('Item Code') + '::90',
        _('Subscription Item Name') + '::150',
        _('Expires On') + ':Date:90',
        _('Expiry (In Days)') + ':Int:60',
        _('Lifetime') + '::60',
        _('Ref Subscription') + ':Link/Gym Subscription:120',
        _('Status') + '::90',
    ]
    return columns


def make_conditions(filters={}):
    conds = []
    if filters.get('member'):
        conds.append(
            "s.member = '{}'".format(filters.get('member'))
        )
    if filters.get('subscription_item'):
        conds.append(
            "si.item_code = '{}'".format(filters.get('subscription_item'))
        )
    if filters.get('subscription_status'):
        conds.append(
            "s.status = '{}'".format(filters.get('status'))
        )
    return conds


def query_data(conditions):
    items_grp = """
        SELECT
            s.member AS member,
            si.item_code AS item_code,
            MAX(s.to_date) AS to_date
        FROM
            `tabGym Subscription Item` AS si,
            `tabGym Subscription` AS s
        WHERE
            {conditions}
            s.docstatus = 1 AND
            s.name = si.parent AND
            si.parentfield = 'service_items'
        GROUP BY s.member, si.item_code
    """.format(
        conditions=' AND '.join(conditions) + ' AND '
        if conditions else '',
    )
    return frappe.db.sql(
        """
            SELECT
                g.member AS member_id,
                s.member_name AS member_name,
                g.item_code AS item_code,
                si.item_name AS item_name,
                g.to_date AS expiry_date,
                s.is_lifetime AS is_lifetime,
                s.name AS subscription,
                s.status AS status
            FROM
                `tabGym Subscription Item` AS si,
                `tabGym Subscription` AS s,
                ({grouped}) AS g
            WHERE
                {conditions}
                g.member = s.member AND
                g.to_date = s.to_date AND
                g.item_code = si.item_code AND
                s.docstatus = 1 AND
                s.name = si.parent AND
                si.parentfield = 'service_items'
        """.format(
            grouped=items_grp,
            conditions=' AND '.join(conditions) + ' AND '
            if conditions else '',
        ),
        as_dict=1,
        debug=1,
    )


def inject_cols(row):
    row_dict = frappe._dict(row)
    if row_dict.expiry_date:
        row_dict.expiry_status = (
            row_dict.expiry_date - frappe.utils.datetime.date.today()
        ).days
    if row_dict.is_lifetime:
        row_dict.lifetime = 'Yes'
    return row_dict


def make_row(row):
    keys = [
        'member_id', 'member_name',
        'item_code', 'item_name',
        'expiry_date', 'expiry_status', 'lifetime',
        'subscription', 'status',
    ]
    return map(lambda x: row.get(x), keys)
