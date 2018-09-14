// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gym Member', {
  setup: function(frm) {
    frm.trigger('set_queries');
  },
  refresh: function(frm) {
    frappe.dynamic_link = {
      doc: frm.doc,
      fieldname: 'name',
      doctype: 'Gym Member',
    };
    frm.toggle_display(
      ['contact_section', 'address_html', 'contact_html', 'emergency_contact'],
      !frm.doc.__islocal
    );
    frm.toggle_enable('customer', frm.doc.__islocal);
    if (!frm.doc.__islocal) {
      frm.trigger('render_address_and_contact');
    } else {
      frappe.contacts.clear_address_and_contact(frm);
    }
  },
  set_queries: function(frm) {
    ['emergency_contact', 'primary_contact'].forEach(contact => {
      frm.set_query(contact, function(doc) {
        return {
          query:
            'psd_customization.fitness_world.api.gym_member.get_member_contacts',
          filters: { member: doc.name },
        };
      });
    });
  },
  render_address_and_contact: function(frm) {
    frappe.contacts.render_address_and_contact(frm);
    function make_dialog(doctype) {
      return new frappe.ui.Dialog({
        title: `Select ${doctype}`,
        fields: [{ fieldname: 'docname', fieldtype: 'Link', options: doctype }],
        primary_action: async function() {
          await frappe.call({
            method:
              'psd_customization.fitness_world.api.gym_member.link_member_to_doctype',
            args: {
              member: frm.doc['name'],
              doctype,
              docname: this.get_value('docname'),
            },
          });
          frm.reload_doc();
          this.hide();
        },
      });
    }

    const address_dialog = make_dialog('Address');
    const $link_btn_address = $(
      '<button class="btn btn-xs btn-default btn-link-address">Link Address</button>'
    ).on('click', function() {
      address_dialog.show();
    });
    $(frm.fields_dict['address_html'].wrapper)
      .find('.btn-address')
      .after($link_btn_address);

    const contact_dialog = make_dialog('Contact');
    const $link_btn_contact = $(
      '<button class="btn btn-xs btn-default btn-link-contact">Link Contact</button>'
    ).on('click', function() {
      contact_dialog.show();
    });
    $(frm.fields_dict['contact_html'].wrapper)
      .find('.btn-contact')
      .unbind('click')
      .on('click', function() {
        frappe.new_doc('Contact', {
          first_name: frm.doc['first_name'],
          last_name: frm.doc['last_name'],
        });
      })
      .after($link_btn_contact);
  },
});
