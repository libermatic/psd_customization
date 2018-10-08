# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from frappe.utils import today

from psd_customization.fitness_world.api.gym_subscription \
    import generate_new_subscriptions_on


def daily():
    posting_date = today()
    generate_new_subscriptions_on(posting_date)
