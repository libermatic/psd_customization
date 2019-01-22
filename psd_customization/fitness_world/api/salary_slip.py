# -*- coding: utf-8 -*-
# Copyright (c) 2019, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, add_days, cint, flt
from builtins import str
import json
from functools import partial
from toolz import merge, pluck, compose

from psd_customization.utils.datetime import month_diff


@frappe.whitelist()
def set_trainings_in_salary_slip(doc_json, set_in_response=0):
    doc = (
        frappe.get_doc(json.loads(doc_json)) if isinstance(doc_json, str) else doc_json
    )
    if not doc.salary_structure:
        joining_date, relieving_date = frappe.db.get_value(
            "Employee", doc.employee, ["date_of_joining", "relieving_date"]
        )
        doc.salary_structure = doc.check_sal_struct(joining_date, relieving_date)
    structure = frappe.get_doc("Salary Structure", doc.salary_structure)
    doc.salary_slip_based_on_training = structure.salary_slip_based_on_training
    doc.set("trainings", [])
    if doc.salary_slip_based_on_training:
        trainings = get_trainings_for_salary_slip(doc.employee, doc.end_date)
        for row in trainings:
            doc.append(
                "trainings",
                {
                    "training": row.name,
                    "member_name": row.gym_member_name,
                    "months": row.months,
                    "subscription": row.gym_subscription,
                    "cost_multiplier": row.cost_multiplier or 1.0,
                },
            )
        doc.actual_training_months = compose(sum, partial(pluck, "months"))(trainings)
        doc.total_training_months = compose(
            sum,
            partial(map, lambda t: flt(t.months or 0) * flt(t.cost_multiplier or 1)),
        )(trainings)
        doc.training_rate = structure.training_monthly_rate
        add_earning_for_training(
            doc,
            structure.training_salary_component,
            doc.total_training_months * doc.training_rate,
        )
    if cint(set_in_response):
        frappe.response.docs.append(doc)


def get_trainings_for_salary_slip(employee, end_date):
    trainer = frappe.db.exists("Gym Trainer", {"employee": employee})
    if not trainer:
        return []
    trainings = frappe.db.sql(
        """
            SELECT
                ta.name AS name,
                s.member_name AS gym_member_name,
                s.name AS gym_subscription,
                ta.salary_till AS salary_till,
                ta.from_date AS from_date,
                ta.to_date AS to_date,
                s.cost_multiplier AS cost_multiplier
            FROM `tabTrainer Allocation` AS ta
            LEFT JOIN `tabGym Subscription` AS s
                ON s.name = ta.gym_subscription
            WHERE
                ta.gym_trainer = %(trainer)s AND
                IFNULL(
                    ta.salary_till,
                    DATE_SUB(ta.from_date, INTERVAL 1 DAY)
                ) < %(end_date)s AND
                DATEDIFF(
                    ta.to_date,
                    IFNULL(
                        ta.salary_till,
                        DATE_SUB(ta.from_date, INTERVAL 1 DAY)
                    )
                ) > 0
        """,
        values={"trainer": trainer, "end_date": end_date},
        as_dict=1,
    )
    return map(_set_days(end_date), trainings)


def add_earning_for_training(doc, salary_component, amount):
    for row in doc.earnings or []:
        if row.salary_component == salary_component:
            row.amount = amount
            return
    doc.append(
        "earnings",
        {
            "salary_component": salary_component,
            "abbr": frappe.db.get_value(
                "Salary Component", salary_component, "salary_component_abbr"
            ),
            "amount": amount,
        },
    )


def _set_days(end_date):
    def fn(row):
        from_date = add_days(row.salary_till, 1) if row.salary_till else row.from_date
        to_date = min(getdate(end_date), row.to_date)
        return frappe._dict(
            merge(row, {"months": month_diff(from_date, to_date, as_dec=1)})
        )

    return fn


@frappe.whitelist()
def get_training_data(training, start_date, end_date):
    trainer_alloc = frappe.get_doc("Trainer Allocation", training)
    if trainer_alloc:
        ta = _set_days(end_date)(frappe._dict(trainer_alloc.as_dict()))
        cost_multiplier = frappe.db.get_value(
            "Gym Subscription", ta.gym_subscription, "cost_multiplier"
        )
        return {
            "months": ta.months,
            "gym_subscription": ta.gym_subscription,
            "cost_multiplier": cost_multiplier or 1.0,
        }


def training_query(doctype, txt, searchfield, start, page_len, filters):
    trainer = frappe.db.exists("Gym Trainer", {"employee": filters.get("employee")})
    if not trainer:
        return []
    return frappe.db.sql(
        """
            SELECT name, gym_member_name
            FROM `tabTrainer Allocation`
            WHERE
                gym_trainer = %(trainer)s AND
                (salary_till IS NULL OR salary_till < to_date)
            ORDER BY to_date
            LIMIT %(start)s, %(page_len)s
        """,
        values={"trainer": trainer, "start": start, "page_len": page_len},
    )
