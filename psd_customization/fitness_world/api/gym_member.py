# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

import frappe
from functools import partial
from erpnext.accounts.party import get_party_account
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from toolz import pluck, compose, first, drop


def get_member_contacts(doctype, txt, searchfield, start, page_len, filters):
    Contact = frappe.qb.DocType("Contact")
    DynamicLink = frappe.qb.DocType("Dynamic Link")
    return (
        frappe.qb.from_(Contact)
        .left_join(DynamicLink)
        .on(DynamicLink.parent == Contact.name)
        .where(
            (DynamicLink.link_name == filters.get("member"))
            & (DynamicLink.link_doctype == "Gym Member")
        )
    ).run()


@frappe.whitelist()
def link_member_to_doctype(member, doctype, docname):
    link_doc = frappe.get_doc(doctype, docname)
    if link_doc:
        make_links = compose(
            partial(map, lambda x: x.get("link_name")),
            partial(filter, lambda x: x.get("link_doctype") == "Gym Member"),
        )
        if member not in make_links(link_doc.links):
            link_doc.append(
                "links", {"link_doctype": "Gym Member", "link_name": member}
            )
            link_doc.save()
    return link_doc


@frappe.whitelist()
def get_number_from_contact(contact):
    numbers = frappe.get_all(
        "Contact Phone",
        filters={"parent": contact, "is_primary_mobile_no": 1},
        pluck="phone",
        limit=1,
    )
    return numbers[0] if numbers else None


def _make_new_pe(member):
    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Receive"
    pe.party_type = "Customer"
    pe.party = member.customer
    pe.party_name = member.member_name
    company = frappe.db.get_value("Gym Settings", None, "default_company")
    pe.party_account = get_party_account("Customer", member.customer, company)
    pe.paid_from = pe.party_account
    return pe


@frappe.whitelist()
def make_payment_entry(source_name):
    member = frappe.get_doc("Gym Member", source_name)
    invoices = frappe.get_all(
        "Sales Invoice",
        filters=[
            ["customer", "=", member.customer],
            ["docstatus", "=", "1"],
            ["status", "!=", "Paid"],
        ],
    )
    pes = compose(
        list,
        partial(map, lambda x: get_payment_entry("Sales Invoice", x)),
        partial(pluck, "name"),
    )(invoices)
    pe = first(pes) if pes else _make_new_pe(member)
    for entry in drop(1, pes):
        pe.set("paid_amount", pe.paid_amount + entry.paid_amount)
        pe.set("received_amount", pe.received_amount + entry.received_amount)
        for ref in entry.references:
            pe.append("references", ref)
    pe.set_amounts()
    return pe
