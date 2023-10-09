# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import Order
from frappe.utils import getdate, add_days, formatdate


def _generate_intervals(start_date, end_date, allocations):
    if not allocations:
        return [{"from_date": start_date, "to_date": end_date}]
    intervals = []
    cur_start = start_date
    for a in allocations:
        if getdate(cur_start) < getdate(a.get("from_date")):
            intervals.append(
                {"from_date": cur_start, "to_date": add_days(a.get("from_date"), -1)}
            )
        intervals.append(a)
        cur_start = add_days(a.get("to_date"), 1)
    if getdate(intervals[-1]["to_date"]) < getdate(end_date):
        intervals.append(
            {"from_date": add_days(intervals[-1]["to_date"], 1), "to_date": end_date}
        )
    return intervals


@frappe.whitelist()
def get_schedule(subscription, item=None):
    sub_start, sub_end = frappe.db.get_value(
        "Gym Subscription", subscription, ["from_date", "to_date"]
    )
    allocations = frappe.get_all(
        "Trainer Allocation",
        filters={"gym_subscription": subscription},
        fields=[
            "name",
            "gym_trainer",
            "gym_trainer_name",
            "from_date",
            "to_date",
            "training_slot",
        ],
        order_by="from_date",
    )
    return _generate_intervals(sub_start, sub_end, allocations)


@frappe.whitelist()
def create(subscription, trainer, from_date, to_date, slot=None):
    allocation = frappe.get_doc(
        {
            "doctype": "Trainer Allocation",
            "gym_subscription": subscription,
            "gym_trainer": trainer,
            "from_date": from_date,
            "to_date": to_date,
            "training_slot": slot,
        }
    ).insert(ignore_permissions=True)
    return allocation


def _get_field(key):
    if key == "slot":
        return "training_slot"
    if key in ["from_date", "to_date"]:
        return key
    return None


@frappe.whitelist()
def update(name, key, value):
    allocation = frappe.get_doc("Trainer Allocation", name)
    field = _get_field(key)
    if field in ["from_date", "to_date"]:
        if allocation.salary_till and getdate(value) < allocation.salary_till:
            return frappe.throw(
                "Cannot update. Freezed till {}".format(
                    formatdate(allocation.salary_till)
                )
            )
    if field:
        allocation.flags.ignore_permissions = True
        allocation.set(field, value)
        allocation.save()
    return allocation


@frappe.whitelist()
def remove(name):
    return frappe.delete_doc("Trainer Allocation", name, ignore_permissions=True)


@frappe.whitelist()
def get_last(member, item_code=None, subscription_item=None):
    _subscription_item = subscription_item or frappe.db.get(
        "Gym Subscription Item",
        filters={"disabled": 0, "item": item_code, "requires_trainer": 1},
    )

    if not _subscription_item:
        return None

    GymSubscription = frappe.qb.DocType("Gym Subscription")
    subscription_sub = (
        frappe.qb.from_(GymSubscription)
        .select(
            GymSubscription.name,
        )
        .where(
            (GymSubscription.subscription_item == _subscription_item.name)
            & (GymSubscription.member == member)
            & (GymSubscription.docstatus == 1)
        )
        .orderby(GymSubscription.from_date, order=Order.desc)
        .limit(1)
    )
    TrainerAllocation = frappe.qb.DocType("Trainer Allocation")
    allocations = (
        frappe.qb.from_(TrainerAllocation)
        .select(
            TrainerAllocation.gym_trainer,
            TrainerAllocation.gym_trainer_name,
            TrainerAllocation.training_slot,
        )
        .where(TrainerAllocation.gym_subscription == subscription_sub)
        .orderby(TrainerAllocation.to_date, order=Order.desc)
        .limit(1)
    ).run(as_dict=1)

    if allocations:
        return allocations[0]

    return None
