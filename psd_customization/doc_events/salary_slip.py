# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.utils import getdate

from psd_customization.fitness_world.api.salary_slip \
    import set_trainings_in_salary_slip


def before_insert(doc, method):
    if not doc.trainings:
        set_trainings_in_salary_slip(doc)


def on_submit(doc, method):
    if doc.salary_slip_based_on_training:
        for training in doc.trainings:
            allocation = frappe.get_doc(
                'Trainer Allocation', training.training,
            )
            allocation.flags.ignore_permissions = True
            allocation.salary_till = min(
                getdate(doc.end_date), allocation.to_date
            )
            allocation.save()


def on_cancel(doc, method):
    if doc.salary_slip_based_on_training:
        for training in doc.trainings:
            last_salary_slip = frappe.db.sql(
                """
                    SELECT ss.end_date
                    FROM `tabSalary Slip Training` AS sst
                    LEFT JOIN `tabSalary Slip` AS ss
                        ON ss.name = sst.parent
                    WHERE
                        ss.docstatus = 1 AND
                        ss.name != %(name)s AND
                        sst.training = %(training)s
                    ORDER BY ss.end_date DESC
                    LIMIT 1
                """,
                values={
                    'name': doc.name,
                    'training': training.training,
                },
            )
            allocation = frappe.get_doc(
                'Trainer Allocation', training.training,
            )
            allocation.flags.ignore_permissions = True
            allocation.salary_till = last_salary_slip[0][0] \
                if last_salary_slip else None
            allocation.save()
