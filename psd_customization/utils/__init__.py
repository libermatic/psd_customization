# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import date_diff, today, cint


def pretty_date(iso_datetime):
    """
        Extends frappe.utils.data.pretty_date
    """
    days = date_diff(iso_datetime, today)
    if days < 0:
        return frappe.utils.pretty_date(iso_datetime)
    if days < 1:
        return _('today')
    if days == 1:
        return _('tomorrow')
    if days < 7:
        return _('in {} days'.format(cint(days)))
    if days < 12:
        return _('in a week')
    if days < 31:
        return _('in {} weeks'.format(cint(days / 7.0)))
    if days < 46:
        return _('in a month')
    if days < 365:
        return _('in {} months'.format(cint(days / 30.0)))
    if days < 550:
        return _('in a year')
    return _('in {} years'.format(cint(days / 365.0)))
