# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate
from functools import partial
from toolz import compose, get, concatv, merge, pluck


_columns = [
    {"key": "trainer", "label": _("Trainer ID") + ":Link/Gym Trainer:120"},
    {"key": "trainer_name", "label": _("Trainer Name") + "::180"},
    {"key": "slot", "label": _("Slot") + ":Link/Training Slot:120"},
    {"key": "shift", "label": _("Shift") + "::90"},
    {"key": "member", "label": _("Member ID") + ":Link/Gym Member:120"},
    {"key": "member_name", "label": _("Member Name") + "::180"},
    {"key": "from_date", "label": _("Training Start") + ":Date:90"},
    {"key": "to_date", "label": _("Training End") + ":Date:90"},
    {"key": "subscription", "label": _("Subscription") + ":Link/Gym Subscription:120"},
    {"key": "subscription_status", "label": _("Subscription Status") + "::90"},
]


def execute(filters=None):
    columns = get_columns(_columns)
    data = get_data(filters)
    return columns, data


get_columns = compose(list, partial(pluck, "label"))

get_keys = compose(list, partial(pluck, "key"))


def add_filter_clause(filters, field):
    def fn(clauses):
        if filters.get(field):
            if field == "from_date":
                clause = ["ta.to_date >= %(from_date)s"]
            elif field == "to_date":
                clause = ["ta.from_date <= %(to_date)s"]
            else:
                clause = ["ta.{field} = %({field})s".format(field=field)]
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
    init_clauses, init_values = [], {}
    filter_composer = make_filter_composer(
        filters, ["gym_trainer", "training_slot", "from_date", "to_date"]
    )
    make_clauses = filter_composer(add_filter_clause)
    make_values = filter_composer(add_filter_value)
    return (" AND ".join(make_clauses(init_clauses)), make_values(init_values))


def get_data(filters):
    clauses, values = make_conditions(filters)
    allocations = frappe.db.sql(
        """
            SELECT
                ta.gym_subscription AS subscription,
                s.status AS subscription_status,
                s.to_date AS subscription_end,
                m.name AS member,
                m.member_name AS member_name,
                ta.gym_trainer AS trainer,
                ta.gym_trainer_name AS trainer_name,
                ta.from_date AS from_date,
                ta.to_date AS to_date,
                ta.training_slot AS slot,
                ts.shift AS shift
            FROM `tabTrainer Allocation` AS ta
            LEFT JOIN `tabGym Member` AS m
                ON ta.gym_member = m.name
            LEFT JOIN `tabGym Subscription` AS s
                ON ta.gym_subscription = s.name
            LEFT JOIN `tabTraining Slot` AS ts
                ON ta.training_slot = ts.name
            {where}
            ORDER BY ta.from_date
        """.format(
            where="WHERE {}".format(clauses) if clauses else ""
        ),
        values=values,
        as_dict=1,
    )
    make_row = compose(
        partial(get, get_keys(_columns)), _set_subscription_status(getdate())
    )
    return list(map(make_row, allocations))


def _set_subscription_status(today):
    def fn(row):
        subscription_end = row.get("subscription_end")
        subscription_status = (
            "Expired"
            if subscription_end and subscription_end < today
            else row.get("subscription_status")
        )
        return merge(row, {"subscription_status": subscription_status})

    return fn
