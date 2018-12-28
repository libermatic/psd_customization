# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial
from toolz import compose, get, concatv, merge


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    columns = [
        _('Trainer ID') + ':Link/Gym Trainer:120',
        _('Trainer Name') + '::180',
        _('Slot') + ':Link/Training Slot:120',
        _('Member ID') + ':Link/Gym Member:120',
        _('Member Name') + '::180',
        _('Subscription') + ':Link/Gym Subscription:120',
        _('From') + ':Date:90',
        _('To') + ':Date:90',
    ]
    return columns


def add_filter_clause(filters, field):
    def fn(clauses):
        if filters.get(field):
            if field == 'from_date':
                clause = ['ta.to_date >= %(from_date)s']
            elif field == 'to_date':
                clause = ['ta.from_date <= %(to_date)s']
            else:
                clause = ['ta.{field} = %({field})s'.format(field=field)]
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
        return compose(
            *map(
                lambda field: add_fn(filters, field),
                fields,
            )
        )
    return fn


def make_conditions(filters):
    init_clauses, init_values = ['ta.gym_member = m.name'], {}
    filter_composer = make_filter_composer(
        filters, ['gym_trainer', 'training_slot', 'from_date', 'to_date']
    )
    make_clauses = filter_composer(add_filter_clause)
    make_values = filter_composer(add_filter_value)
    return (
        " AND ".join(make_clauses(init_clauses)),
        make_values(init_values),
    )


def get_data(filters):
    clauses, values = make_conditions(filters)
    allocations = frappe.db.sql(
        """
            SELECT
                ta.gym_subscription AS subscription,
                m.name AS member,
                m.member_name AS member_name,
                ta.gym_trainer AS trainer,
                ta.gym_trainer_name AS trainer_name,
                ta.from_date AS from_date,
                ta.to_date AS to_date,
                ta.training_slot AS slot
            FROM
                `tabTrainer Allocation` AS ta, `tabGym Member` AS m
            WHERE {clauses}
            ORDER BY ta.from_date
        """.format(clauses=clauses),
        values=values,
        as_dict=1,
    )
    make_row = compose(
        partial(get, [
            'trainer', 'trainer_name', 'slot',
            'member', 'member_name', 'subscription',
            'from_date', 'to_date',
        ])
    )
    return map(make_row, allocations)
