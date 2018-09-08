# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from functools import reduce
from frappe.model.document import Document

from psd_customization.fitness_world.api.gym_fee import (
    get_next_from_date, get_to_date, get_items
)


class GymFee(Document):
    def before_save(self):
        if not self.from_date:
            self.from_date = get_next_from_date(self.membership)
        if not self.duration:
            self.duration = 1
        if not self.to_date:
            self.to_date = get_to_date(
                self.membership, self.from_date, self.duration
            )
        if not self.items:
            map(
                lambda item: self.append('items', item),
                get_items(self.membership, self.duration),
            )
        self.total_amount = reduce(lambda a, x: a + x.amount, self.items, 0)
