# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import add_days, add_months, getdate, cint, today, flt
from erpnext.accounts.doctype.payment_entry.payment_entry \
    import get_payment_entry
from erpnext.accounts.doctype.pricing_rule.pricing_rule \
    import get_pricing_rule_for_item
from functools import partial
from toolz import pluck, compose, get, first, merge

from psd_customization.utils.fp import pick
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
    si.run_method('calculate_taxes_and_totals')
    return si


def _existing_subscription(member, item_code=None):
    if item_code:
        return frappe.db.sql(
            """
                SELECT mi.end_date AS to_date
                FROM
                    `tabGym Subscription Item` AS mi,
                    `tabGym Subscription` AS ms
                WHERE
                    mi.parent = ms.name AND
                    mi.item_code = '{item_code}' AND
                    ms.docstatus = 1 AND
                    ms.member = '{member}'
                ORDER BY mi.end_date DESC
                LIMIT 1
            """.format(member=member, item_code=item_code),
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
    return frappe.db.get_value('Gym Member', member, 'enrollment_date')


def get_to_date(from_date, frequency):
    if frequency == 'Lifetime':
        return None
    make_end_of_freq = compose(
        partial(add_days, days=-1), partial(add_months, from_date)
    )
    freq_map = {
        'Monthly': 1,
        'Quaterly': 3,
        'Half-Yearly': 6,
        'Yearly': 12,
    }
    return make_end_of_freq(freq_map[frequency])


@frappe.whitelist()
def get_items(member, subscription_plan, transaction_date=None):
    plan = frappe.get_doc('Gym Subscription Plan', subscription_plan)
    existing_subscriptions = _existing_subscription(member)

    def update_amounts(item):
        price = get_item_price(
            item.get('item_code'),
            member=member,
            transaction_date=transaction_date,
            no_pricing_rule=0,
        )
        return merge(
            item,
            {'rate': price, 'amount': price * item.get('qty', 0)}
        )

    def update_dates(item):
        if cint(item.get('one_time')):
            return item
        next_date = get_next_from_date(member, item.get('item_code'))
        return merge(
            item,
            {
                'start_date': next_date,
                'end_date': get_to_date(next_date, plan.frequency),
            }
        )

    pick_fields = compose(
        partial(pick, [
            'item_code', 'item_name',
            'qty', 'rate', 'amount', 'one_time',
            'start_date', 'end_date',
        ]),
        update_dates,
        update_amounts,
        lambda x: x.as_dict()
    )

    make_items = compose(
        partial(map, pick_fields),
        partial(filter, lambda x: not existing_subscriptions or not x.one_time),
    )
    return make_items(plan.items) if plan else None


@frappe.whitelist()
def get_item_price(
    item_code,
    member=None,
    company=None,
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
    if not member:
        return frappe.throw('Cannot fetch price without Member')
    applied_pricing_rule = get_pricing_rule_for_item(frappe._dict({
        'item_code': item_code,
        'transaction_type': 'selling',
        'customer': frappe.db.get_value('Gym Member', member, 'customer'),
        'price_list': price_list,
        'company': company or frappe.db.get_value(
            'Gym Settings', None, 'default_company'
        ) or frappe.defaults.get_user_default('company'),
        'transaction_date': transaction_date or today(),
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
