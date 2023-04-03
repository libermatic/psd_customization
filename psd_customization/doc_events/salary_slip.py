import frappe
from frappe.utils import getdate
from frappe.query_builder import Order

from psd_customization.fitness_world.api.salary_slip import set_trainings_in_salary_slip


def before_insert(doc, method):
    if not doc.trainings:
        set_trainings_in_salary_slip(doc)


def on_submit(doc, method):
    if doc.salary_slip_based_on_training:
        for training in doc.trainings:
            allocation = frappe.get_doc(
                "Trainer Allocation",
                training.training,
            )
            allocation.flags.ignore_permissions = True
            allocation.salary_till = min(getdate(doc.end_date), allocation.to_date)
            allocation.save()


def on_cancel(doc, method):
    if doc.salary_slip_based_on_training:
        SalarySlipTraining = frappe.qb.Doctype("Salary Slip Training")
        SalarySlip = frappe.qb.Doctype("Salary Slip")
        for training in doc.trainings:
            last_salary_slip = (
                frappe.qb.from_(SalarySlipTraining)
                .left_join(SalarySlip)
                .on(SalarySlip.name == SalarySlipTraining.parent)
                .select(SalarySlip.end_date)
                .where(
                    (SalarySlip.docstatus == 1)
                    & (SalarySlip.name != doc.name)
                    & (SalarySlipTraining.training == training.training)
                )
                .orderby(SalarySlip.end_date, order=Order.desc)
                .limit(1)
            ).run()
            allocation = frappe.get_doc(
                "Trainer Allocation",
                training.training,
            )
            allocation.flags.ignore_permissions = True
            allocation.salary_till = (
                last_salary_slip[0][0] if last_salary_slip else None
            )
            allocation.save()
