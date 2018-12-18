# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils \
    import add_days, getdate, cint, today, date_diff
from erpnext.accounts.doctype.payment_entry.payment_entry \
    import get_payment_entry
from functools import partial
from toolz import compose, merge, concat, pluck

from psd_customization.utils.datetime \
    import merge_intervals, pretty_date, month_diff
from psd_customization.utils.fp import compact
from sms_extras.api.sms import get_sms_text, request_sms


@frappe.whitelist()
def make_payment_entry(source_name):
    reference_invoice = frappe.db.get_value(
        'Gym Subscription', source_name, 'reference_invoice'
    )
    return get_payment_entry('Sales Invoice', reference_invoice)


@frappe.whitelist()
def make_sales_invoice(source_name):
    subscription = frappe.get_doc('Gym Subscription', source_name)
    settings = frappe.get_single('Gym Settings')
    si = frappe.new_doc('Sales Invoice')
    args = {
        'gym_member': subscription.member,
        'gym_member_name': subscription.member_name,
        'customer': frappe.db.get_value(
            'Gym Member', subscription.member, 'customer'
        ),
        'company': settings.default_company,
        'naming_series': settings.naming_series,
        'taxes_and_charges': settings.default_tax_template,
    }
    for field, value in args.iteritems():
        si.set(field, value)
    si.append('items', {
        'item_code': subscription.subscription_item,
        'qty': 60 if subscription.is_lifetime else month_diff(
            subscription.from_date, subscription.to_date, as_dec=1
        ),
        'is_gym_subscription': 1,
        'gym_is_lifetime': subscription.is_lifetime,
        'gym_subscription': subscription.name,
        'gym_from_date': subscription.from_date,
        'gym_to_date': subscription.to_date,
    })
    si.run_method('set_missing_values')
    si.run_method('set_taxes')
    si.run_method('calculate_taxes_and_totals')
    return si


def dispatch_sms(subscription, template_field):
    doc = frappe.get_doc('Gym Subscription', subscription)
    template = frappe.db.get_value('Gym Settings', None, template_field)
    mobile_no = frappe.db.get_value(
        'Gym Member', doc.member, 'notification_number'
    )
    if template and mobile_no:
        content = get_sms_text(template, doc)
        if content:
            request_sms(mobile_no, content, communication={
                'subject': 'SMS: {} for {}'.format(template, doc.member),
                'reference_doctype': 'Gym Subscription',
                'reference_name': doc.name,
                'timeline_doctype': 'Gym Member',
                'timeline_name': doc.member,
            })


def send_reminders(posting_date=today()):
    settings = frappe.get_single('Gym Settings')
    if not settings.sms_before_expiry and not settings.sms_on_expiry:
        return None
    days_before_expiry = compose(
        tuple,
        partial(map, lambda x: add_days(posting_date, cint(x))),
        compact,
    )(settings.days_before_expiry.split('\n'))
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
        values={
            'posting_date': posting_date,
            'days_before_expiry': days_before_expiry,
        },
        as_dict=1,
    )
    for sub in subscriptions:
        template = settings.sms_on_expiry \
            if date_diff(sub.get('to_date'), posting_date) < 0 \
            else settings.sms_before_expiry
        try:
            content = get_sms_text(
                template,
                merge(sub, {
                    'eta': pretty_date(
                        getdate(sub.get('to_date')),
                        ref_date=getdate(posting_date)
                    )
                }),
            )
            subject = 'SMS: {} for {}'.format(template, sub.get('member'))
            if content:
                request_sms(
                    sub.get('mobile_no'),
                    content,
                    communication={
                        'subject': subject,
                        'reference_doctype': 'Gym Subscription',
                        'reference_name': sub.get('name'),
                        'timeline_doctype': 'Gym Member',
                        'timeline_name': sub.get('member'),
                    }
                )
        except TypeError:
            pass
    return None


def _existing_subscription_by_item(
    member, item_code, start_date, end_date, lifetime, limit=0
):
    filters = [
        "(s.to_date >= '{}' OR s.is_lifetime = 1)".format(start_date)
    ]
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
            filters=" AND ".join(filters),
            limit='LIMIT 1' if limit else '',
        ),
        values={
            'member': member,
            'item_code': item_code,
            'start_date': start_date,
            'end_date': end_date,
        },
        as_dict=True,
    )


def _get_subscriptions(member, item, from_date, to_date, lifetime, limit=0):
    filters = [
        "(to_date >= '{}' OR is_lifetime = 1)".format(from_date)
    ]
    if not lifetime and to_date:
        filters.append("from_date <= '{}'".format(to_date))
    return frappe.db.sql(
        """
            SELECT
                name,
                from_date,
                to_date,
                is_lifetime
            FROM `tabGym Subscription`
            WHERE
                member = '{member}' AND
                subscription_item = '{item}' AND
                docstatus = 1 AND
                {filters}
            ORDER BY from_date
            {limit}
        """.format(
            member=member,
            item=item,
            filters=" AND ".join(filters),
            limit='LIMIT 1' if limit else '',
        ),
        as_dict=1,
    )


def _get_existing_subscription(member, item, from_date, to_date, lifetime):
    try:
        return _get_subscriptions(
            member, item, from_date, to_date, lifetime, limit=1
        )[0]
    except IndexError:
        return None


def _has_valid_requirements(
    member, item_code, from_date, to_date, lifetime, current=None
):
    subscriptions = list(
        concat([
            _get_subscriptions(
                member, item_code, from_date, to_date, lifetime
            ),
            current or [],
        ])
    )
    sort_and_merge = compose(
        merge_intervals,
        partial(sorted, key=lambda x: getdate(x.get('from_date'))),
    )
    try:
        for sub in sort_and_merge(subscriptions):
            if getdate(sub.get('from_date')) <= getdate(from_date) \
                    and getdate(sub.get('to_date')) >= getdate(to_date):
                return True
    except KeyError:
        for sub in subscriptions:
            if sub.get('is_lifetime'):
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

    filter_items = _filter_item(items)
    for item in items:
        existing = subscription_exists(
            item=item.item_code,
            from_date=item.from_date,
            to_date=item.to_date,
            lifetime=item.is_lifetime,
        )
        if existing:
            frappe.throw(
                'Another Subscription - <strong>{subscription}</strong>, for '
                '<strong>{item_name}</strong> already exists during this time '
                'frame.'.format(
                    subscription=existing.get('name'),
                    item_name=item.item_name
                )
            )
    for item in items:
        parents = frappe.get_all(
            'Gym Subscription Item Parent',
            fields=['gym_subscription_item', 'item_name'],
            filters={
                'parent': item.item_code,
                'parentfield': 'parents',
                'parenttype': 'Gym Subscription Item',
            }
        )
        for parent in parents:
            item_code = frappe.db.get_value(
                'Gym Subscription Item',
                parent.get('gym_subscription_item'),
                'item',
            )
            has_requirements = requirements_fulfilled(
                item_code=parent.get('gym_subscription_item'),
                from_date=item.from_date,
                to_date=item.to_date,
                lifetime=item.is_lifetime,
                current=filter_items(item_code),
            )
            if not has_requirements:
                frappe.throw(
                    'Required dependency <strong>{}</strong> not fulfiled for '
                    '<strong>{}</strong>.'.format(
                        parent.get('item_name'), item.item_name
                    )
                )


@frappe.whitelist()
def get_currents(member):
    return frappe.db.sql(
        """
            SELECT
                a.name,
                a.subscription_item AS item,
                a.subscription_name AS item_name,
                a.is_lifetime,
                a.from_date,
                a.to_date
            FROM `tabGym Subscription` AS a
            INNER JOIN (
                SELECT
                    subscription_item,
                    MAX(from_date) AS from_date
                FROM `tabGym Subscription`
                WHERE member=%(member)s AND docstatus=1
                GROUP BY subscription_item
            ) AS b ON
                a.subscription_item = b.subscription_item AND
                a.from_date = b.from_date
            WHERE a.member=%(member)s AND a.docstatus=1
        """,
        values={'member': member},
        as_dict=1,
    )


@frappe.whitelist()
def update_status(subscription, status):
    if status in ['Active', 'Stopped']:
        doc = frappe.get_doc('Gym Subscription', subscription)
        if doc.status == 'Expired':
            return frappe.throw('Cannot set status for expired Subscriptions')
        doc.status = status
        doc.save()


def _set_expiry(subscription):
    doc = frappe.get_doc('Gym Subscription', subscription)
    doc.status = 'Expired'
    doc.save()


def set_expired_susbcriptions(posting_date):
    subscriptions = frappe.get_all(
        'Gym Subscription',
        filters=[
            ['status', '!=', 'Expired'],
            ['is_lifetime', '=', 0],
            ['to_date', '<', posting_date]
        ]
    )
    return compose(
        partial(map, _set_expiry),
        partial(pluck, 'name'),
    )(subscriptions)
