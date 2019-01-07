# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

from psd_customization.fitness_world.api.salary_slip \
    import set_trainings_in_salary_slip


def before_insert(doc, method):
    if not doc.trainings:
        set_trainings_in_salary_slip(doc)
