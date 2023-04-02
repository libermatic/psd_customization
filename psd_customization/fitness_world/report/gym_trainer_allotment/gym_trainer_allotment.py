# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate
from functools import partial
from toolz import compose, get, merge, pluck


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


def get_data(filters):
    TrainerAllocation = frappe.qb.DocType("Trainer Allocation")
    GymMember = frappe.qb.DocType("Gym Member")
    GymSubscription = frappe.qb.DocType("Gym Subscription")
    TrainingSlot = frappe.qb.DocType("Training Slot")
    q = (
        frappe.qb.from_(TrainerAllocation)
        .left_join(GymMember)
        .on(GymMember.name == TrainerAllocation.gym_member)
        .left_join(GymSubscription)
        .on(GymSubscription.name == TrainerAllocation.gym_subscription)
        .left_join(TrainingSlot)
        .on(TrainingSlot.name == TrainerAllocation.training_slot)
        .select(
            TrainerAllocation.gym_subscription.as_("subscription"),
            GymSubscription.status.as_("subscription_status"),
            GymSubscription.to_date.as_("subscription_end"),
            GymMember.name.as_("member"),
            GymMember.member_name,
            TrainerAllocation.gym_trainer.as_("trainer"),
            TrainerAllocation.gym_trainer_name.as_("trainer_name"),
            TrainerAllocation.from_date,
            TrainerAllocation.to_date,
            TrainerAllocation.training_slot.as_("slot"),
            TrainingSlot.shift,
        )
    )

    for field in ["gym_trainer", "training_slot", "from_date", "to_date"]:
        value = filters.get(field)
        if value:
            if field == "from_date":
                q = q.where(TrainerAllocation.to_date >= value)
            elif field == "to_date":
                q = q.where(TrainerAllocation.from_date <= value)
            else:
                q = q.where(GymSubscription[field] == value)

    allocations = q.run(as_dict=True)
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
