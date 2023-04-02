# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.query_builder.functions import Max
from frappe.utils import add_days, getdate, cint, today, date_diff
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from functools import partial
from toolz import compose, merge, concat, pluck, first

from psd_customization.utils.datetime import merge_intervals, pretty_date, month_diff
from psd_customization.utils.fp import compact
from sms_extras.api.sms import get_sms_text, request_sms


@frappe.whitelist()
def make_payment_entry(source_name):
    reference_invoice = frappe.db.get_value(
        "Gym Subscription", source_name, "reference_invoice"
    )
    return get_payment_entry("Sales Invoice", reference_invoice)


@frappe.whitelist()
def make_sales_invoice(source_name):
    subscription = frappe.get_doc("Gym Subscription", source_name)
    settings = frappe.get_single("Gym Settings")
    si = frappe.new_doc("Sales Invoice")
    args = {
        "gym_member": subscription.member,
        "gym_member_name": subscription.member_name,
        "customer": frappe.db.get_value("Gym Member", subscription.member, "customer"),
        "company": settings.default_company,
        "naming_series": settings.naming_series,
        "taxes_and_charges": settings.default_tax_template,
    }
    for field, value in args.items():
        si.set(field, value)
    qty = (
        (
            frappe.db.get_value(
                "Gym Subscription Item",
                subscription.subscription_item,
                "quantity_for_lifetime",
            )
            or 1
        )
        if subscription.is_lifetime
        else month_diff(subscription.from_date, subscription.to_date, as_dec=1)
    )
    si.append(
        "items",
        {
            "item_code": subscription.subscription_item,
            "qty": qty,
            "is_gym_subscription": 1,
            "gym_is_lifetime": subscription.is_lifetime,
            "gym_subscription": subscription.name,
            "gym_from_date": subscription.from_date,
            "gym_to_date": subscription.to_date,
        },
    )
    si.run_method("set_missing_values")
    si.run_method("set_taxes")
    si.run_method("calculate_taxes_and_totals")
    return si


def dispatch_sms(subscription, template_field):
    doc = frappe.get_doc("Gym Subscription", subscription)
    template = frappe.db.get_value("Gym Settings", None, template_field)
    mobile_no = frappe.db.get_value("Gym Member", doc.member, "notification_number")
    if template and mobile_no:
        content = get_sms_text(template, doc)
        if content:
            request_sms(
                mobile_no,
                content,
                communication={
                    "subject": "SMS: {} for {}".format(template, doc.member),
                    "reference_doctype": "Gym Subscription",
                    "reference_name": doc.name,
                    "timeline_doctype": "Gym Member",
                    "timeline_name": doc.member,
                },
            )


def send_reminders(posting_date=today()):
    settings = frappe.get_single("Gym Settings")
    if not settings.sms_before_expiry and not settings.sms_on_expiry:
        return None
    days_before_expiry = compose(
        tuple, partial(map, lambda x: add_days(posting_date, cint(x))), compact
    )(settings.days_before_expiry.split("\n"))
    subscriptions = frappe.db.sql(
        """
            SELECT
                s.name AS name,
                m.name AS member,
                m.member_name AS member_name,
                s.posting_date AS posting_date,
                s.from_date AS from_date,
                s.to_date AS to_date,
                m.notification_number AS mobile_no
            FROM
                `tabGym Subscription` AS s,
                `tabGym Member` AS m
            WHERE
                s.docstatus = 1 AND
                s.status = 'Paid' AND
                s.member = m.name AND
                IFNULL(m.notification_number, '') != '' AND (
                    s.to_date < %(posting_date)s OR
                    s.to_date IN %(days_before_expiry)s
                )
        """,
        values={"posting_date": posting_date, "days_before_expiry": days_before_expiry},
        as_dict=1,
    )
    for sub in subscriptions:
        template = (
            settings.sms_on_expiry
            if date_diff(sub.get("to_date"), posting_date) < 0
            else settings.sms_before_expiry
        )
        try:
            content = get_sms_text(
                template,
                merge(
                    sub,
                    {
                        "eta": pretty_date(
                            getdate(sub.get("to_date")), ref_date=getdate(posting_date)
                        )
                    },
                ),
            )
            subject = "SMS: {} for {}".format(template, sub.get("member"))
            if content:
                request_sms(
                    sub.get("mobile_no"),
                    content,
                    communication={
                        "subject": subject,
                        "reference_doctype": "Gym Subscription",
                        "reference_name": sub.get("name"),
                        "timeline_doctype": "Gym Member",
                        "timeline_name": sub.get("member"),
                    },
                )
        except TypeError:
            pass
    return None


def _existing_subscription_by_item(
    member, item_code, start_date, end_date, lifetime, limit=0
):
    filters = ["(s.to_date >= '{}' OR s.is_lifetime = 1)".format(start_date)]
    if not lifetime and end_date:
        filters.append("s.from_date <= '{}'".format(end_date))
    return frappe.db.sql(
        """
            SELECT
                s.name AS subscription,
                s.is_lifetime AS is_lifetime,
                s.from_date AS from_date,
                s.to_date AS to_date
            FROM
                `tabGym Subscription Item` AS si,
                `tabGym Subscription` AS s
            WHERE
                si.item_code = %(item_code)s AND
                si.parentfield = 'service_items' AND
                si.parent = s.name AND
                s.docstatus = 1 AND
                s.member = %(member)s AND
                {filters}
            ORDER BY s.from_date
            {limit}
        """.format(
            filters=" AND ".join(filters), limit="LIMIT 1" if limit else ""
        ),
        values={
            "member": member,
            "item_code": item_code,
            "start_date": start_date,
            "end_date": end_date,
        },
        as_dict=True,
    )


def _get_subscriptions(member, item, from_date, to_date, lifetime, limit=0, status=[]):
    GymSubscription = frappe.qb.DocType("Gym Subscription")
    q = (
        frappe.qb.from_(GymSubscription)
        .select(
            GymSubscription.name,
            GymSubscription.from_date,
            GymSubscription.to_date,
            GymSubscription.is_lifetime,
        )
        .where(
            (GymSubscription.member == member)
            & (GymSubscription.subscription_item == item)
            & (GymSubscription.status.isin(status or ["Active"]))
            & (GymSubscription.docstatus == 1)
            & (
                (GymSubscription.to_date >= from_date)
                | (GymSubscription.is_lifetime == 1)
            )
        )
        .orderby(GymSubscription.from_date)
    )
    if not lifetime and to_date:
        q = q.where(GymSubscription.from_date <= to_date)
    if limit:
        q = q.limit(1)

    return q.run(as_dict=1)


def _get_existing_subscription(member, item, from_date, to_date, lifetime):
    try:
        return _get_subscriptions(member, item, from_date, to_date, lifetime, limit=1)[
            0
        ]
    except IndexError:
        return None


def _has_valid_requirements(
    member, item_code, from_date, to_date, lifetime, current=None
):
    subscriptions = list(
        concat(
            [
                _get_subscriptions(
                    member,
                    item_code,
                    from_date,
                    to_date,
                    lifetime,
                    status=["Active", "Expired"],
                ),
                current or [],
            ]
        )
    )
    for sub in subscriptions:
        if sub.is_lifetime:
            return True
    sort_and_merge = compose(
        merge_intervals, partial(sorted, key=lambda x: x.from_date)
    )
    try:
        for sub in sort_and_merge(subscriptions):
            if (
                sub.from_date
                and sub.from_date <= from_date
                and sub.to_date
                and sub.to_date >= to_date
            ):
                return True
    except IndexError:
        pass
    return False


def _filter_item(items):
    def fn(item_code):
        return filter(lambda x: x.item_code == item_code, items)

    return fn


def validate_dependencies(member, items):
    subscription_exists = partial(_get_existing_subscription, member=member)
    requirements_fulfilled = partial(_has_valid_requirements, member=member)

    filter_items = compose(list, _filter_item(items))
    for item in items:
        existing = subscription_exists(
            item=item.item_code,
            from_date=item.from_date,
            to_date=item.to_date,
            lifetime=item.is_lifetime,
        )
        if existing:
            frappe.throw(
                "Another Subscription - <strong>{subscription}</strong>, for "
                "<strong>{item_name}</strong> already exists during this time "
                "frame.".format(
                    subscription=existing.get("name"), item_name=item.item_name
                )
            )
    for item in items:
        parents = frappe.get_all(
            "Gym Subscription Item Parent",
            fields=["gym_subscription_item", "item_name"],
            filters={
                "parent": item.item_code,
                "parentfield": "parents",
                "parenttype": "Gym Subscription Item",
            },
        )
        for parent in parents:
            item_code = frappe.db.get_value(
                "Gym Subscription Item", parent.get("gym_subscription_item"), "item"
            )
            has_requirements = requirements_fulfilled(
                item_code=parent.get("gym_subscription_item"),
                from_date=item.from_date,
                to_date=item.to_date,
                lifetime=item.is_lifetime,
                current=filter_items(item_code),
            )
            if not has_requirements:
                frappe.throw(
                    "Required dependency <strong>{}</strong> not fulfiled for "
                    "<strong>{}</strong>.".format(
                        parent.get("item_name"), item.item_name
                    )
                )


@frappe.whitelist()
def get_currents(member):
    GymSubscription = frappe.qb.DocType("Gym Subscription")
    latest_sub = (
        frappe.qb.from_(GymSubscription)
        .select(
            GymSubscription.subscription_item,
            Max(GymSubscription.from_date).as_("from_date"),
        )
        .where((GymSubscription.member == member) & (GymSubscription.docstatus == 1))
        .groupby(GymSubscription.subscription_item)
    ).as_("latest_sub")

    return (
        frappe.qb.from_(GymSubscription)
        .select(
            GymSubscription.name,
            GymSubscription.status,
            GymSubscription.subscription_item.as_("item"),
            GymSubscription.subscription_name.as_("item_name"),
            GymSubscription.is_training,
            GymSubscription.is_lifetime,
            GymSubscription.from_date,
            GymSubscription.to_date,
        )
        .inner_join(latest_sub)
        .on(
            (latest_sub.subscription_item == GymSubscription.subscription_item)
            & (latest_sub.from_date == GymSubscription.from_date)
        )
        .where((GymSubscription.member == member) & (GymSubscription.docstatus == 1))
    ).run(as_dict=1)


@frappe.whitelist()
def get_current_trainable(member):
    try:
        return compose(
            first, partial(filter, lambda x: cint(x.is_training)), get_currents
        )(member)
    except StopIteration:
        return None


@frappe.whitelist()
def update_status(subscription, status):
    if status in ["Active", "Stopped"]:
        doc = frappe.get_doc("Gym Subscription", subscription)
        if doc.status == "Expired":
            return frappe.throw("Cannot set status for expired Subscriptions")
        doc.status = status
        doc.save()


def _set_expiry(subscription):
    doc = frappe.get_doc("Gym Subscription", subscription)
    doc.status = "Expired"
    doc.save()


def set_expired_susbcriptions(posting_date):
    subscriptions = frappe.get_all(
        "Gym Subscription",
        filters=[
            ["docstatus", "=", 1],
            ["status", "!=", "Expired"],
            ["is_lifetime", "=", 0],
            ["to_date", "<", posting_date],
        ],
    )
    return compose(list, partial(map, _set_expiry), partial(pluck, "name"))(
        subscriptions
    )
