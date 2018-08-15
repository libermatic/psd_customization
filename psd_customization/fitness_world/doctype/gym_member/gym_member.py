# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
from frappe.contacts.address_and_contact import load_address_and_contact


class GymMember(Document):
    def onload(self):
        load_address_and_contact(self)
