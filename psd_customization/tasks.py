# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from frappe.utils import today

from psd_customization.fitness_world.api.gym_subscription \
    import send_reminders


def daily():
    posting_date = today()
    send_reminders(posting_date)
