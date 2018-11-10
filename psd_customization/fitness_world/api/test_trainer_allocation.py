# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and Contributors
# See license.txt
from __future__ import unicode_literals
import unittest
from frappe.utils import getdate

from psd_customization.fitness_world.api.trainer_allocation import (
    _generate_intervals
)


class TestGenerateIntervals(unittest.TestCase):
    def test_generate_intervals_empty(self):
        actual = _generate_intervals('2018-06-16', '2018-07-15', [])
        expected = [{'from_date': '2018-06-16', 'to_date': '2018-07-15'}]
        self.assertEqual(actual, expected)

    def test_generate_intervals_same_start(self):
        actual = _generate_intervals('2018-06-16', '2018-07-15', [
            {'from_date': '2018-06-16', 'to_date': '2018-06-20'},
        ])
        expected = [
            {'from_date': '2018-06-16', 'to_date': '2018-06-20'},
            {'from_date': '2018-06-21', 'to_date': '2018-07-15'},
        ]
        self.assertEqual(actual, expected)

    def test_generate_intervals_same_end(self):
        actual = _generate_intervals('2018-06-16', '2018-07-15', [
            {'from_date': '2018-06-20', 'to_date': '2018-07-15'},
        ])
        expected = [
            {'from_date': '2018-06-16', 'to_date': '2018-06-19'},
            {'from_date': '2018-06-20', 'to_date': '2018-07-15'},
        ]
        self.assertEqual(actual, expected)

    def test_generate_intervals_filled(self):
        actual = _generate_intervals('2018-06-16', '2018-07-15', [
            {'from_date': '2018-06-16', 'to_date': '2018-06-20'},
            {'from_date': '2018-06-21', 'to_date': '2018-06-30'},
            {'from_date': '2018-07-01', 'to_date': '2018-07-15'},
        ])
        expected = [
            {'from_date': '2018-06-16', 'to_date': '2018-06-20'},
            {'from_date': '2018-06-21', 'to_date': '2018-06-30'},
            {'from_date': '2018-07-01', 'to_date': '2018-07-15'},
        ]
        self.assertEqual(actual, expected)

    def test_generate_intervals_filled_single(self):
        actual = _generate_intervals('2018-06-16', '2018-07-15', [
            {'from_date': '2018-06-16', 'to_date': '2018-07-15'},
        ])
        expected = [
            {'from_date': '2018-06-16', 'to_date': '2018-07-15'},
        ]
        self.assertEqual(actual, expected)

    def test_generate_intervals_between_dates(self):
        actual = _generate_intervals('2018-06-16', '2018-07-15', [
            {'from_date': '2018-06-21', 'to_date': '2018-06-30'},
        ])
        expected = [
            {'from_date': '2018-06-16', 'to_date': '2018-06-20'},
            {'from_date': '2018-06-21', 'to_date': '2018-06-30'},
            {'from_date': '2018-07-01', 'to_date': '2018-07-15'},
        ]
        self.assertEqual(actual, expected)

    def test_generate_intervals_empty_middle(self):
        actual = _generate_intervals('2018-06-16', '2018-07-15', [
            {'from_date': '2018-06-16', 'to_date': '2018-06-20'},
            {'from_date': '2018-07-01', 'to_date': '2018-07-15'},
        ])
        expected = [
            {'from_date': '2018-06-16', 'to_date': '2018-06-20'},
            {'from_date': '2018-06-21', 'to_date': '2018-06-30'},
            {'from_date': '2018-07-01', 'to_date': '2018-07-15'},
        ]
        self.assertEqual(actual, expected)

    def test_generate_intervals_injects_interval_props(self):
        actual = _generate_intervals('2018-06-16', '2018-07-15', [
            {'from_date': '2018-06-21', 'to_date': '2018-06-30', 'x': 'inj'},
        ])
        expected = [
            {'from_date': '2018-06-16', 'to_date': '2018-06-20'},
            {'from_date': '2018-06-21', 'to_date': '2018-06-30', 'x': 'inj'},
            {'from_date': '2018-07-01', 'to_date': '2018-07-15'},
        ]
        self.assertEqual(actual, expected)
