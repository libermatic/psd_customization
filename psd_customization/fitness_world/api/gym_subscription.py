# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils \
    import add_days, add_months, getdate, cint, today, flt, date_diff
from erpnext.accounts.doctype.payment_entry.payment_entry \
    import get_payment_entry
from erpnext.accounts.doctype.pricing_rule.pricing_rule \
    import get_pricing_rule_for_item
from functools import partial
from toolz import pluck, compose, get, first, merge

from psd_customization.utils.fp import pick, compact
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
    si = frappe.new_doc('Sales Invoice')
    si.gym_subscription = source_name
    si.customer = frappe.db.get_value(
        'Gym Member', subscription.member, 'customer'
    )

    def get_description(item):
        if not item.start_date:
            return item.item_name
        return '{item_name}: Valid from {start_date} to {end_date}'.format(
            item_name=item.item_name,
            start_date=item.get_formatted('start_date'),
            end_date=item.get_formatted('end_date'),
        )
    for item in subscription.items:
        si.append('items', {
            'item_code': item.item_code,
            'description': get_description(item),
            'qty': item.qty,
            'rate': item.rate,
        })

    settings = frappe.get_single('Gym Settings')
    si.company = settings.default_company
    si.naming_series = settings.naming_series
    si.taxes_and_charges = settings.default_tax_template
    si.run_method('set_missing_values')
    si.run_method('set_taxes')
    si.run_method('calculate_taxes_and_totals')
    return si


def _existing_subscription(
    member, item_code=None, start_date=None, end_date=None
):
    if item_code and start_date and end_date:
        return frappe.db.sql(
            """
                SELECT
                    s.name AS subscription,
                    s.from_date AS from_date,
                    s.to_date AS to_date
                FROM
                    `tabGym Subscription Item` AS si,
                    `tabGym Subscription` AS s
                WHERE
                    si.item_code = '{item_code}' AND
                    si.parentfield = 'service_items' AND
                    si.parent = s.name AND
                    s.docstatus = 1 AND
                    s.member = '{member}' AND
                    s.from_date <= '{end_date}' AND
                    s.to_date >= '{start_date}'
                LIMIT 1
            """.format(
                member=member,
                item_code=item_code,
                start_date=start_date,
                end_date=end_date,
            ),
            as_dict=True,
        )
    return frappe.db.sql(
        """
            SELECT to_date FROM `tabGym Subscription`
            WHERE docstatus = 1 AND member = '{member}'
            ORDER BY to_date DESC
            LIMIT 1
        """.format(member=member),
        as_dict=True,
    )


@frappe.whitelist()
def get_next_from_date(member, item_code=None):
    existing_subscriptions = _existing_subscription(member, item_code)
    if existing_subscriptions:
        return compose(
            partial(add_days, days=1),
            getdate,
            partial(get, 'to_date'),
            first,
        )(existing_subscriptions)
    membership = _get_uninvoiced_membership(member)
    if membership:
        return membership.start_date
    return frappe.db.get_value('Gym Member', member, 'enrollment_date')


@frappe.whitelist()
def get_next_period(member, item_code=None):
    next_start = get_next_from_date(member, item_code)
    next_end = get_to_date(next_start, 'Monthly')
    return {
        'from_date': next_start,
        'to_date': next_end,
    }


def get_to_date(from_date, frequency):
    if frequency == 'Lifetime':
        return None
    make_end_of_freq = compose(
        partial(add_days, days=-1), partial(add_months, from_date)
    )
    freq_map = {
        'Monthly': 1,
        'Quarterly': 3,
        'Half-Yearly': 6,
        'Yearly': 12,
    }
    return make_end_of_freq(freq_map[frequency])


def _get_uninvoiced_membership(member):
    uninvoiced_memberships = frappe.db.sql(
        """
            SELECT name FROM `tabGym Membership`
            WHERE docstatus = 1 AND IFNULL(status, '') = ''
            AND member = %(member)s
            LIMIT 1
        """,
        values={'member': member},
        as_dict=1,
    )
    if not uninvoiced_memberships:
        return None
    return compose(
        lambda x: frappe.get_doc('Gym Membership', x) if x else None,
        first,
        partial(pluck, 'name'),
    )(uninvoiced_memberships)


def _get_membership_items():
    default_item_group = frappe.db.get_value(
        'Gym Settings', None, 'default_item_group'
    )
    return pluck(
        'name',
        frappe.get_all(
            'Item',
            filters={
                'item_group': default_item_group,
                'disabled': 0,
                'is_gym_membership_item': 1,
            }
        ),
    ) if default_item_group else []


def _make_item(member, transaction_date):
    def update_amounts(item):
        price = get_item_price(
            item.get('item_code'),
            member=member,
            transaction_date=transaction_date or today(),
            no_pricing_rule=0,
        )
        return merge(
            {'qty': 1},
            item,
            {'rate': price, 'amount': price * item.get('qty', 1)},
        )
    pick_fields = partial(pick, [
        'item_code', 'item_name',
        'qty', 'uom', 'rate', 'amount',
    ])
    return compose(pick_fields, update_amounts)


@frappe.whitelist()
def get_membership_items(member, transaction_date=None):
    make_membership_items = compose(
        partial(
            map,
            lambda x: merge(x, {'qty': 1, 'uom': x.get('stock_uom')}),
        ),
        partial(
            map,
            lambda x: frappe.get_value(
                'Item', x, ['item_code', 'item_name', 'stock_uom'], as_dict=1
            )
        ),
        _get_membership_items,
    )
    make_items_list = partial(map, _make_item(member, transaction_date))
    return compose(make_items_list, make_membership_items)() \
        if _get_uninvoiced_membership(member) else None


@frappe.whitelist()
def get_item_price(
    item_code,
    member=None,
    qty=0,
    transaction_date=None,
    price_list='Standard Selling',
    no_pricing_rule=1
):
    prices = frappe.db.sql(
        """
            SELECT price_list_rate FROM `tabItem Price`
            WHERE price_list = '{price_list}' AND item_code = '{item_code}'
        """.format(item_code=item_code, price_list=price_list)
    )
    price_list_rate = prices[0][0] if prices else 0
    if cint(no_pricing_rule):
        return price_list_rate
    applied_pricing_rule = get_pricing_rule_for_item(frappe._dict({
        'doctype': 'Gym Subscription Item',
        'transaction_type': 'selling',
        'transaction_date': transaction_date or today(),
        'qty': qty,
        'item_code': item_code,
        'customer': frappe.db.get_value('Gym Member', member, 'customer'),
        'price_list': price_list,
        'conversion_factor': 1,
        'conversion_rate': 1.0,
        'company': frappe.db.get_value(
            'Gym Settings', None, 'default_company'
        ) or frappe.defaults.get_user_default('company'),
    }))
    return applied_pricing_rule.get('price_list_rate') or \
        price_list_rate * (1 - flt(
            applied_pricing_rule.get('discount_percentage', 0)
        ) / 100)


def get_subscription_by_invoice(invoice):
    invoices = frappe.db.sql(
        """
            SELECT name FROM `tabGym Subscription`
            WHERE docstatus = 1 AND reference_invoice = '{invoice}'
        """.format(invoice=invoice),
        as_dict=True,
    )
    get_one_subscription = compose(
        partial(frappe.get_doc, 'Gym Subscription'),
        partial(get, 'name'),
        first,
    )
    return get_one_subscription(invoices) if invoices else None


def _make_gym_subscription(member, posting_date, do_not_submit=True):
    subscription = frappe.new_doc('Gym Subscription')
    subscription.member = member
    subscription.posting_date = posting_date
    subscription.insert()
    if not do_not_submit:
        subscription.submit()
    return subscription


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


def generate_new_subscriptions_on(posting_date=today()):
    members = pluck('name', frappe.get_all(
        'Gym Member',
        filters={
            'docstatus': 1,
            'status': 'Active',
            'auto_renew': 'Yes',
        }
    ))
    do_not_submit = not frappe.db.get_value(
        'Gym Settings', None, 'submit_auto_renew'
    )
    for member in members:
        if get_next_from_date(member) == getdate(posting_date):
            subscription = _make_gym_subscription(
                member, posting_date, do_not_submit
            )
            frappe.logger(__name__).debug(
                'Gym Subscription {} ({}) generated'.format(
                    subscription.name, posting_date
                )
            )
            dispatch_sms(subscription.name, 'sms_invoiced')


def send_reminders(posting_date=today()):
    settings = frappe.get_single('Gym Settings')
    if not settings.sms_before_expiry and not settings.sms_on_expiry:
        return None
    days_before_expiry = compose(
        tuple,
        partial(map, lambda x: add_days(posting_date, cint(x))),
        compact,
    )(settings.days_before_expiry.split('\n'))
    members_sub_query = """
        SELECT name FROM `tabGym Member`
        WHERE status != 'Stopped' AND IFNULL(notification_number, '') != ''
    """

    items_sub_query = """
        SELECT
            si.item_code AS item_code,
            si.item_name AS item_name,
            si.end_date AS expiry_date,
            s.name AS subscription,
            s.member AS member,
            m.notification_number AS mobile_no
        FROM
            `tabGym Subscription Item` AS si,
            `tabGym Subscription` AS s,
            `tabGym Member` AS m
        WHERE
            s.docstatus = 1 AND
            s.name = si.parent AND
            m.name = s.member AND
            si.one_time != 1 AND
            s.member IN ({members_sub_query})
    """.format(members_sub_query=members_sub_query)
    items_grp_sub_query = """
        SELECT
            si.item_code AS item_code,
            MAX(si.end_date) AS expiry_date,
            s.member AS member
        FROM
            `tabGym Subscription Item` AS si,
            `tabGym Subscription` AS s
        WHERE
            s.docstatus = 1 AND
            s.name = si.parent AND
            si.one_time != 1
        GROUP BY si.item_code, s.member
    """
    query = frappe.db.sql(
        """
            SELECT
                il.item_code AS item_code,
                il.item_name AS item_name,
                il.member AS member,
                il.mobile_no AS mobile_no,
                ig.expiry_date AS expiry_date,
                il.subscription AS subscription
            FROM
                ({items_grp_sub_query}) AS ig,
                ({items_sub_query}) AS il
            WHERE
                ig.item_code = il.item_code AND
                ig.member = il.member AND
                ig.expiry_date = il.expiry_date AND (
                    ig.expiry_date < %s OR ig.expiry_date IN %s
                )
        """.format(
            items_grp_sub_query=items_grp_sub_query,
            items_sub_query=items_sub_query,
        ),
        values=(
            posting_date,
            days_before_expiry,
        ),
        as_dict=1,
    )
    for item in query:
        template = settings.sms_on_expiry \
            if date_diff(item.get('expiry_date'), posting_date) < 0 else \
            settings.sms_before_expiry
        try:
            content = get_sms_text(template, item)
            subject = 'SMS: {} for {}'.format(template, item.get('member'))
            if content:
                request_sms(
                    item.get('mobile_no'),
                    content,
                    communication={
                        'subject': subject,
                        'reference_doctype': 'Gym Subscription',
                        'reference_name': item.get('subscription'),
                        'timeline_doctype': 'Gym Member',
                        'timeline_name': item.get('member'),
                    }
                )
            pass
        except TypeError:
            pass
    return None
def get_existing_subscription(member, item_code, start_date, end_date):
    try:
        return _existing_subscription(
            member, item_code, start_date, end_date
        )[0]
    except IndexError:
        return None


def has_valid_subscription(member, item_code, start_date, end_date):
    periods = frappe.db.sql(
        """
            SELECT
                s.from_date AS from_date,
                s.to_date AS to_date
            FROM
                `tabGym Subscription Item` AS si,
                `tabGym Subscription` AS s
            WHERE
                si.item_code = '{item_code}' AND
                si.parentfield = 'service_items' AND
                si.parent = s.name AND
                s.docstatus = 1 AND
                s.member = '{member}' AND
                s.from_date <= '{end_date}' AND
                s.to_date >= '{start_date}'
            ORDER BY s.from_date
        """.format(
            member=member,
            item_code=item_code,
            start_date=start_date,
            end_date=end_date,
        ),
        as_dict=True,
    )
    try:
        for interval in merge_intervals(periods):
            if interval.get('from_date') <= getdate(start_date) \
                    and getdate(interval.get('to_date')) >= getdate(end_date):
                return True
    except IndexError:
        pass
    return False
