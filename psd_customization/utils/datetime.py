# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import date_diff, flt, getdate, cint, add_months, add_days, datetime
from functools import partial
from toolz import compose


def _get_next_start(d):
    x = 1
    while True:
        yield add_months(d, months=x), x
        x += 1


def _get_next_end(d):
    x = 1
    while True:
        yield compose(partial(add_days, days=-1), partial(add_months, months=x))(d), x
        x += 1


def month_diff(d1, d2, as_dec=0):
    first_start = getdate(d1)
    last_start = getdate(add_days(d2, 1))
    assert first_start < last_start
    next_start, months = first_start, 0
    cur_start, cur_months = first_start, 0
    gen_start = _get_next_start(first_start)
    while next_start <= last_start:
        cur_start, cur_months = next_start, months
        next_start, months = next(gen_start)
    rem_days = date_diff(last_start, cur_start)
    if cint(as_dec):
        days_in_month = date_diff(next_start, cur_start)
        return cur_months + flt(rem_days) / flt(days_in_month)
    return cur_months, rem_days


def merge_intervals(intervals):
    reduced = [intervals[0]]
    if not reduced[0].get("from_date") or not reduced[0].get("to_date"):
        raise KeyError()
    for interval in intervals[1:]:
        from_date, to_date = interval["from_date"], interval["to_date"]
        if add_days(reduced[-1]["to_date"], 1) == from_date:
            reduced[-1]["to_date"] = to_date
        else:
            reduced.append(interval)

    return reduced


def pretty_date(iso_datetime, ref_date=None):
    """
        Extends frappe.utils.data.pretty_date
    """
    days = date_diff(iso_datetime, ref_date or datetime.date.today())
    if days < 0:
        return frappe.utils.pretty_date(iso_datetime)
    if days < 1:
        return _("today")
    if days == 1:
        return _("tomorrow")
    if days < 7:
        return _("in {} days".format(cint(days)))
    if days < 12:
        return _("in a week")
    if days < 31:
        return _("in {} weeks".format(cint(days / 7.0)))
    if days < 46:
        return _("in a month")
    if days < 365:
        return _("in {} months".format(cint(days / 30.0)))
    if days < 550:
        return _("in a year")
    return _("in {} years".format(cint(days / 365.0)))
