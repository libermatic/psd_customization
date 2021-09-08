# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial
from toolz import compose, assoc, get, merge, concatv


def execute(filters=None):
    return (
        get_columns(),
        compose(list, partial(filter, status_filter(filters)), partial(map, make_row))(
            get_data(filters)
        ),
    )


def get_columns():
    columns = [
        _("Member ID") + ":Link/Gym Member:120",
        _("Member Name") + "::180",
        _("Subscription Item") + "::90",
        _("Item Name") + "::150",
        _("Stated On") + ":Date:90",
        _("Expires On") + ":Date:90",
        _("Expiry (In Days)") + ":Int:60",
        _("Lifetime") + "::60",
        _("Status") + "::90",
    ]
    return columns


def add_filter_clause(filters, field):
    def fn(clauses):
        if filters.get(field):
            clause = ["a.{field}=%({field})s".format(field=field)]
            return concatv(clauses, clause)
        return clauses

    return fn


def add_filter_value(filters, field):
    def fn(values):
        if filters.get(field):
            value = {field: filters.get(field)}
            return merge(values, value)
        return values

    return fn


def make_filter_composer(filters, fields):
    def fn(add_fn):
        return compose(*map(lambda field: add_fn(filters, field), fields))

    return fn


def make_conditions(filters):
    init_clauses, init_values = ["a.docstatus=1"], {}
    filter_composer = make_filter_composer(filters, ["member", "subscription_item"])
    make_clauses = filter_composer(add_filter_clause)
    make_values = filter_composer(add_filter_value)
    return (" AND ".join(make_clauses(init_clauses)), make_values(init_values))


def get_data(filters):
    clauses, values = make_conditions(filters)
    return frappe.db.sql(
        """
            SELECT
                a.member AS member,
                a.member_name AS member_name,
                a.subscription_item AS item,
                a.subscription_name AS item_name,
                a.from_date AS start_date,
                a.to_date AS expiry_date,
                a.is_lifetime,
                a.status AS raw_status
            FROM `tabGym Subscription` AS a
            INNER JOIN (
                SELECT
                    member,
                    subscription_item,
                    MAX(from_date) AS from_date
                FROM `tabGym Subscription`
                WHERE docstatus = 1
                GROUP BY member, subscription_item
            ) AS b ON
                a.member = b.member AND
                a.subscription_item = b.subscription_item AND
                a.from_date = b.from_date
            WHERE {clauses}
        """.format(
            clauses=clauses
        ),
        values=values,
        as_dict=1,
    )


def make_row(row):
    lifetime = "Yes" if row.get("is_lifetime") else ""
    expiry_in_days = (
        (row.get("expiry_date") - frappe.utils.datetime.date.today()).days
        if row.get("expiry_date")
        else 0
    )

    def get_status():
        if not row.get("is_lifetime") and expiry_in_days < 0:
            return "Expired"
        return row.get("raw_status")

    add_lifetime = partial(assoc, key="lifetime", value=lifetime)
    set_expiry_eta = partial(assoc, key="expiry_in_days", value=expiry_in_days)
    set_status = partial(assoc, key="status", value=get_status())

    keys = [
        "member",
        "member_name",
        "item",
        "item_name",
        "start_date",
        "expiry_date",
        "expiry_in_days",
        "lifetime",
        "status",
    ]
    return compose(partial(get, keys), set_status, set_expiry_eta, add_lifetime)(row)


def status_filter(filters):
    def fn(row):
        if filters.get("status"):
            return row[-1] == filters.get("status")
        return True

    return fn
