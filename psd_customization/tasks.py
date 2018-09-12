# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from frappe.utils import today

from psd_customization.fitness_world.api.gym_membership \
    import generate_new_fees_on


def daily():
    posting_date = today()
    generate_new_fees_on(posting_date)
