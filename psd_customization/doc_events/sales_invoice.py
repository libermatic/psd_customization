# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from psd_customization.fitness_world.api.gym_fee import get_fee_by_invoice


def on_cancel(doc, method):
    fee = get_fee_by_invoice(doc.name)
    if fee:
        fee.cancel()
