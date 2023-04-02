# -*- coding: utf-8 -*-
# Copyright (c) 2019, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.query_builder import Interval
from frappe.query_builder.functions import IfNull
from frappe.utils import getdate, add_days, cint, flt
from builtins import str
import json
from functools import partial
from toolz import merge, pluck, compose

from psd_customization.utils.fp import mapr


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

    TrainerAllocation = frappe.qb.DocType("Trainer Allocation")
    GymSubscription = frappe.qb.DocType("Gym Subscription")
    trainings = (
        frappe.qb.from_(TrainerAllocation)
        .left_join(GymSubscription)
        .on(GymSubscription.name == TrainerAllocation.gym_subscription)
        .select(
            TrainerAllocation.name,
            GymSubscription.member_name.as_("gym_member_name"),
            GymSubscription.name.as_("gym_subscription"),
            TrainerAllocation.salary_till,
            TrainerAllocation.from_date,
            TrainerAllocation.to_date,
            GymSubscription.day_fraction,
            GymSubscription.cost_multiplier,
        )
        .where(
            (TrainerAllocation.gym_trainer == trainer)
            & (
                IfNull(
                    TrainerAllocation.salary_till,
                    TrainerAllocation.from_date - Interval(days=1),
                )
                < end_date
            )
            & (
                TrainerAllocation.to_date
                - IfNull(
                    TrainerAllocation.salary_till,
                    TrainerAllocation.from_date - Interval(days=1),
                )
                > 0
            )
        )
    ).run(as_dict=1)
    return mapr(_set_days(end_date), trainings)


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
        days = (to_date - from_date).days + 1
        return frappe._dict(merge(row, {"months": days * row.day_fraction}))

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

    TrainerAllocation = frappe.qb.DocType("Trainer Allocation")
    return (
        frappe.qb.from_(TrainerAllocation)
        .select(TrainerAllocation.name, TrainerAllocation.gym_member_name)
        .where(
            (TrainerAllocation.gym_trainer == trainer)
            & (
                TrainerAllocation.salary_till.isnull()
                | (TrainerAllocation.salary_till < TrainerAllocation.to_date)
            )
        )
        .orderby(TrainerAllocation.to_date)
        .limit(page_len)
        .offset(start)
    ).run()
