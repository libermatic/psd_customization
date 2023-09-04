from frappe.utils import today

from psd_customization.fitness_world.api.gym_subscription import (
    set_expired_susbcriptions,
)


def daily():
    posting_date = today()
    set_expired_susbcriptions(posting_date)
