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
      frm.trigger('render_membership_details');
      frm.trigger('add_actions');
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
  render_membership_details: function(frm) {
    if (frm.doc.__onload && frm.doc.__onload['membership_details']) {
      const {
        total_invoices,
        unpaid_invoices,
        outstanding,
        end_date,
      } = frm.doc.__onload['membership_details'];
      const { auto_renew } = frm.doc;
      frm.dashboard.add_section(
        frappe.render_template('gym_member_dashboard', {
          invoices: {
            color: unpaid_invoices ? 'orange' : 'green',
            total: total_invoices || '-',
            unpaid: unpaid_invoices || '-',
          },
          outstanding: {
            color: outstanding ? 'orange' : 'lightblue',
            amount: outstanding
              ? format_currency(
                  outstanding,
                  frappe.defaults.get_default('currency')
                )
              : '-',
          },
          validity: {
            color: moment().isSameOrBefore(end_date || undefined)
              ? 'lightblue'
              : 'red',
            end_date: end_date ? frappe.datetime.str_to_user(end_date) : '-',
          },
          renew: {
            color: auto_renew === 'Yes' ? 'lightblue' : 'darkgrey',
            text: { Yes: 'Auto', No: 'Manual' }[auto_renew] || '-',
          },
        })
      );
    }
  },

  add_actions: function(frm) {
    function get_status_props(status) {
      if (status === 'Active') {
        return {
          label: 'Stop Membership',
          method: 'psd_customization.fitness_world.api.gym_member.stop',
        };
      }
      if (status === 'Stopped' || status === 'Expired') {
        return {
          label: 'Resume Membership',
          method: 'psd_customization.fitness_world.api.gym_member.resume',
        };
      }
      return null;
    }
    function get_renew_props(auto_renew) {
      return {
        label:
          auto_renew === 'Yes' ? 'Disable Auto-Renew' : 'Enable Auto-Renew',
        method: 'psd_customization.fitness_world.api.gym_member.set_auto_renew',
        args: { auto_renew: auto_renew === 'Yes' ? 'No' : 'Yes' },
      };
    }
    frm
      .add_custom_button('Make Payment', function() {
        frappe.model.open_mapped_doc({
          frm,
          method:
            'psd_customization.fitness_world.api.gym_member.make_payment_entry',
        });
      })
      .toggleClass(
        'btn-primary',
        frm.doc.__onload && !!frm.doc.__onload['unpaid_invoices']
      );
    const status_props = get_status_props(frm.doc['status']);
    if (status_props) {
      frm.add_custom_button(
        status_props.label,
        async function() {
          await frappe.call({
            method: status_props.method,
            args: { name: frm.doc['name'] },
          });
          frm.reload_doc();
        },
        'Manage'
      );
    }
    const renew_props = get_renew_props(frm.doc['auto_renew']);
    frm.add_custom_button(
      renew_props.label,
      async function() {
        await frappe.call({
          method: renew_props.method,
          args: { name: frm.doc['name'], ...renew_props.args },
        });
        frm.reload_doc();
      },
      'Manage'
    );
  },
});
