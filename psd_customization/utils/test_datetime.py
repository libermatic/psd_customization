# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and Contributors
# See license.txt
from __future__ import unicode_literals
import unittest
from frappe.utils import getdate

from psd_customization.utils.datetime import (
    month_diff, merge_intervals, pretty_date
)


class TestMonthDiff(unittest.TestCase):
    def test_month_diff(self):
        actual = month_diff('2018-06-15', '2018-06-30')
        expected = (0, 15)
        self.assertEqual(actual, expected)

    def test_month_diff_raises_when_end_date_is_before(self):
        with self.assertRaises(AssertionError):
            month_diff('2018-06-15', '2018-06-05')

    def test_month_diff_decimal(self):
        actual = month_diff('2018-06-15', '2018-06-30', as_dec=1)
        expected = 0.5
        self.assertEqual(actual, expected)

    def test_month_diff_whole(self):
        actual = month_diff('2018-06-15', '2018-07-15', as_dec=1)
        expected = 1.0
        self.assertEqual(actual, expected)

    def test_month_diff_fraction(self):
        actual = month_diff('2018-05-15', '2018-06-30', as_dec=1)
        expected = 1.5
        self.assertEqual(actual, expected)


class TestMergeIntervals(unittest.TestCase):
    def test_merge_intervals(self):
        actual = merge_intervals([
            {'from_date': '2018-06-15', 'to_date': '2018-07-09'},
            {'from_date': '2018-07-10', 'to_date': '2018-07-30'},
        ])
        expected = [{'from_date': '2018-06-15', 'to_date': '2018-07-30'}]
        self.assertEqual(actual, expected)

    def test_merge_intervals_raises_when_list_is_empty(self):
        with self.assertRaises(IndexError):
            merge_intervals([])

    def test_merge_intervals_raises_when_reqd_fields_missing(self):
        with self.assertRaises(KeyError):
            merge_intervals([
                {'from_date': '2018-06-15', 'to_date': '2018-06-30'},
                {'from_date': '2018-07-10'},
            ])
        with self.assertRaises(KeyError):
            merge_intervals([
                {'from_date': '2018-06-15', 'to_date': '2018-06-30'},
                {'to_date': '2018-07-30'},
            ])

    def test_merge_intervals_discontinuous(self):
        actual = merge_intervals([
            {'from_date': '2018-05-05', 'to_date': '2018-05-20'},
            {'from_date': '2018-05-21', 'to_date': '2018-06-04'},
            {'from_date': '2018-06-15', 'to_date': '2018-07-09'},
            {'from_date': '2018-07-10', 'to_date': '2018-07-30'},
        ])
        expected = [
            {'from_date': '2018-05-05', 'to_date': '2018-06-04'},
            {'from_date': '2018-06-15', 'to_date': '2018-07-30'},
        ]
        self.assertEqual(actual, expected)


class TestPrettyDate(unittest.TestCase):
    def test_pretty_date_today(self):
        self.assertEqual(
            pretty_date(getdate('2018-08-19'), getdate('2018-08-19')),
            'today'
        )

    def test_pretty_date_tomorrow(self):
        self.assertEqual(
            pretty_date(getdate('2018-08-20'), getdate('2018-08-19')),
            'tomorrow'
        )

    def test_pretty_date_days(self):
        self.assertEqual(
            pretty_date(getdate('2018-08-25'), getdate('2018-08-19')),
            'in 6 days'
        )

    def test_pretty_date_week(self):
        self.assertEqual(
            pretty_date(getdate('2018-08-29'), getdate('2018-08-19')),
            'in a week'
        )

    def test_pretty_date_weeks(self):
        self.assertEqual(
            pretty_date(getdate('2018-09-05'), getdate('2018-08-19')),
            'in 2 weeks'
        )

    def test_pretty_date_month(self):
        self.assertEqual(
            pretty_date(getdate('2018-09-25'), getdate('2018-08-19')),
            'in a month'
        )

    def test_pretty_date_months(self):
        self.assertEqual(
            pretty_date(getdate('2018-10-25'), getdate('2018-08-19')),
            'in 2 months'
        )

    def test_pretty_date_year(self):
        self.assertEqual(
            pretty_date(getdate('2019-10-25'), getdate('2018-08-19')),
            'in a year'
        )

    def test_pretty_date_years(self):
        self.assertEqual(
            pretty_date(getdate('2020-10-25'), getdate('2018-08-19')),
            'in 2 years'
        )
