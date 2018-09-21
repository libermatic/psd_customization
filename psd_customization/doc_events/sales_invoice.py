# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from psd_customization.fitness_world.api.gym_membership \
    import get_membership_by_invoice


def on_cancel(doc, method):
    membership = get_membership_by_invoice(doc.name)
    if membership:
        membership.cancel()
