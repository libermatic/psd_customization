# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe.core.doctype.sms_settings.sms_settings \
    import get_contact_number, send_sms

from psd_customization.fitness_world.doctype.gym_settings.gym_settings \
    import get_sms_text
from psd_customization.utils.fp import pick


def on_submit(doc, method):
    if doc.subscription:
        if doc.contact_person:
            mobile_no = get_contact_number(
                doc.contact_person, 'Customer', doc.customer,
            )
            text = get_sms_text(
                'invoiced',
                pick(
                    ['name', 'customer_name', 'posting_date', 'due_date'],
                    doc.as_dict(),
                ),
            )
            if mobile_no and text:
                # fix for json.loads casting to int during number validation
                send_sms('"{}"'.format(mobile_no), text)
