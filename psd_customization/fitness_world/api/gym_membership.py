# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint
from functools import partial
from toolz import pluck, compose, first


@frappe.whitelist()
def set_status(name, status):
    if not status:
        frappe.throw('Cannot process blank status')
    membership = frappe.get_doc('Gym Membership', name)
    membership.status = status
    membership.save()


def get_membership_by(member, start_date=None, end_date=None):
    more_args = ''
    if start_date and not end_date:
        more_args = "AND '{0}' BETWEEN start_date AND IFNULL(end_date, '{0}')"\
            .format(start_date)
    if start_date and end_date:
        more_args = \
            "AND start_date <= '{end_date}' AND end_date >= '{start_date}'" \
            .format(start_date, end_date)
    memberships = frappe.db.sql(
        """
            SELECT name FROM `tabGym Membership`
            WHERE docstatus = 1 AND status = 'Active' AND member = %(member)s
            %(more_args)s
            LIMIT 1
        """ % {
            'member': "'{}'".format(member),
            'more_args': more_args,
        },
        as_dict=1,
    )
    if memberships:
        return frappe.get_doc('Gym Membership', memberships[0]['name'])
    return None
@frappe.whitelist()
def get_uninvoiced_membership(member, only_name=0):
    uninvoiced_memberships = frappe.db.sql(
        """
            SELECT name FROM `tabGym Membership`
            WHERE docstatus = 1
            AND member = %(member)s
            AND IFNULL(status, '') = ''
            AND IFNULL(reference_doc, '') = ''
            LIMIT 1
        """,
        values={'member': member},
        as_dict=1,
    )
    if not uninvoiced_memberships:
        return None
    membership = compose(first, partial(pluck, 'name'))(uninvoiced_memberships)
    if cint(only_name):
        return membership
    return frappe.get_doc('Gym Membership', membership) \
        if membership else None
