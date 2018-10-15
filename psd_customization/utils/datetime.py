# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.utils import date_diff, flt, getdate, cint, add_months, add_days
from functools import partial
from toolz import compose


def _get_next_start(d):
    x = 1
    while True:
        yield add_months(d,  months=x), x
        x += 1


def _get_next_end(d):
    x = 1
    while True:
        yield compose(
            partial(add_days, days=-1),
            partial(add_months, months=x),
        )(d), x
        x += 1


def month_diff(d1, d2, as_dec=0):
    start_date = getdate(d1)
    end_date = getdate(d2)
    assert start_date < end_date
    next_start_date, months = start_date, 0
    cur_start_date, cur_months = start_date, 0
    gen_start = _get_next_start(start_date)
    while next_start_date < end_date:
        cur_start_date, cur_months = next_start_date, months
        next_start_date, months = gen_start.next()
    rem_days = date_diff(end_date, cur_start_date)
    if cint(as_dec):
        days_in_month = date_diff(next_start_date, cur_start_date)
        return cur_months + flt(rem_days) / flt(days_in_month)
    return cur_months, rem_days
