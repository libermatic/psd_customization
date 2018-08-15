// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gym Member', {
  refresh: function(frm) {
    frappe.dynamic_link = {
      doc: frm.doc,
      fieldname: 'name',
      doctype: 'Gym Member',
    };
    frm.toggle_display(
      ['contact_section', 'address_html', 'contact_html'],
      !frm.doc.__islocal
    );
    if (!frm.doc.__islocal) {
      frappe.contacts.render_address_and_contact(frm);
    } else {
      frappe.contacts.clear_address_and_contact(frm);
    }
  },
});
