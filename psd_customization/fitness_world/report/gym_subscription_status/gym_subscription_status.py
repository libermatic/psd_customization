# Copyright (c) 2013, Libermatic and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder.functions import Max
from frappe import _
from functools import partial
from toolz import compose, assoc, get


def execute(filters={}):
    return (
        get_columns(),
        compose(list, partial(filter, status_filter(filters)), partial(map, make_row))(
            get_data(filters)
        ),
    )


def get_columns():
    columns = [
        _("Member ID") + ":Link/Gym Member:90",
        _("Member Name") + "::180",
        _("Subscription Item") + "::90",
        _("Item Name") + "::180",
        _("Started On") + ":Date:120",
        _("Expires On") + ":Date:120",
        _("Expiry (In Days)") + ":Int:60",
        _("Lifetime") + "::60",
        _("Status") + "::90",
    ]
    return columns


def get_data(filters):
    GymSubscription = frappe.qb.DocType("Gym Subscription")
    latest_sub = (
        frappe.qb.from_(GymSubscription)
        .select(
            GymSubscription.member,
            GymSubscription.subscription_item,
            Max(GymSubscription.from_date).as_("from_date"),
        )
        .where(GymSubscription.docstatus == 1)
        .groupby(GymSubscription.member, GymSubscription.subscription_item)
    ).as_("latest_sub")
    q = (
        frappe.qb.from_(GymSubscription)
        .right_join(latest_sub)
        .on(
            (latest_sub.member == GymSubscription.member)
            & (latest_sub.subscription_item == GymSubscription.subscription_item)
            & (latest_sub.from_date == GymSubscription.from_date)
        )
        .select(
            GymSubscription.member.as_("member"),
            GymSubscription.member_name,
            GymSubscription.subscription_item.as_("item"),
            GymSubscription.subscription_name.as_("item_name"),
            GymSubscription.from_date.as_("start_date"),
            GymSubscription.to_date.as_("expiry_date"),
            GymSubscription.is_lifetime,
            GymSubscription.status.as_("raw_status"),
        )
        .where((GymSubscription.docstatus == 1))
    )

    for field in ["member", "subscription_item", "status"]:
        value = filters.get(field)
        if value:
            q = q.where(GymSubscription[field] == value)

    if filters.get("between_dates"):
        after_start, before_end = filters.between_dates
        q = q.where(
            (GymSubscription.from_date >= after_start)
            & (GymSubscription.to_date <= before_end)
        )
    return q.run(as_dict=True)


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
