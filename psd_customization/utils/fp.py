# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from functools import reduce
from copy import deepcopy
from toolz import assoc, filter


def compose(*funcs):
    return reduce(lambda f, g: lambda x: f(g(x)), funcs, lambda x: x)


def update(kv_dict):
    def fn(item):
        new_item = deepcopy(item)
        new_item.update(kv_dict)
        return new_item
    return fn


def join(sep):
    def fn(items):
        return sep.join(items)
    return fn


def pick(fields, from_dict):
    def set_field(a, x):
        if from_dict.get(x):
            return assoc(a, x, from_dict.get(x))
        return a
    return reduce(set_field, fields, {})


def compact(iter):
    return filter(None, iter)
