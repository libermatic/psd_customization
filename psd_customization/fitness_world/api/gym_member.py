# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial

from psd_customization.utils.fp import compose


def get_member_contacts(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql(
        """
            SELECT `tabContact`.name
            FROM `tabContact`, `tabDynamic Link`
            WHERE
                `tabContact`.name = `tabDynamic Link`.parent AND
                `tabDynamic Link`.link_name = %(member)s AND
                `tabDynamic Link`.link_doctype = 'Gym Member'
        """, {
            'member': filters.get('member'),
        })


@frappe.whitelist()
def link_member_to_doctype(member, doctype, docname):
    link_doc = frappe.get_doc(doctype, docname)
    if link_doc:
        make_links = compose(
            partial(map, lambda x: x.get('link_name')),
            partial(filter, lambda x: x.get('link_doctype') == 'Gym Member'),
        )
        if member not in make_links(link_doc.links):
            link_doc.append('links', {
                'link_doctype': 'Gym Member', 'link_name': member
            })
            link_doc.save()
    return link_doc


@frappe.whitelist()
def get_members_by_customer(customer):
    members = frappe.get_all('Gym Member', filters={'customer': customer})
    return map(lambda x: x.get('name'), members)
