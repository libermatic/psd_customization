// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gym Member', {
  setup: function(frm) {
    frm.trigger('set_queries');
  },
  refresh: function(frm) {
    frm.toggle_display('member_id', frm.doc.__islocal);
    frm.toggle_enable('enrollment_date', frm.doc.__islocal);
    if (frm.doc.__islocal) {
      frm.set_value('enrollment_date', frappe.datetime.get_today());
    }
    frappe.dynamic_link = {
      doc: frm.doc,
      fieldname: 'name',
      doctype: 'Gym Member',
    };
    frm.toggle_display(
      [
        'contact_section',
        'address_html',
        'contact_html',
        'notification_contact',
        'emergency_contact',
      ],
      !frm.doc.__islocal
    );
    frm.toggle_enable('customer', frm.doc.__islocal);
    if (!frm.doc.__islocal) {
      frm.trigger('render_address_and_contact');
      frm.trigger('render_subscription_details');
      frm.trigger('add_actions');
    } else {
      frappe.contacts.clear_address_and_contact(frm);
    }
  },
  set_queries: function(frm) {
    ['notification_contact', 'emergency_contact'].forEach(contact => {
      frm.set_query(contact, function(doc) {
        return {
          query:
            'psd_customization.fitness_world.api.gym_member.get_member_contacts',
          filters: { member: doc.name },
        };
      });
    });
  },
  notification_contact: async function(frm) {
    if (!frm.doc['notification_contact']) {
      frm.set_value('notification_number', null);
    }
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
        frappe.new_doc('Contact');
      })
      .after($link_btn_contact);
  },
  render_subscription_details: function(frm) {
    if (frm.doc.__onload && frm.doc.__onload['subscription_details']) {
      const {
        total_invoices,
        unpaid_invoices,
        outstanding,
        membership_status,
      } = frm.doc.__onload['subscription_details'];
      const { auto_renew, member_type } = frm.doc;
      frm.dashboard.add_section(
        frappe.render_template('gym_member_dashboard', {
          membership: {
            color:
              membership_status === 'Active'
                ? 'green'
                : membership_status === 'Stopped'
                  ? 'orange'
                  : membership_status === 'Expired'
                    ? 'red'
                    : 'darkgrey',
            text: membership_status || 'None',
          },
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
          renew: {
            color:
              member_type === 'Lifetime' || auto_renew === 'Yes'
                ? 'lightblue'
                : 'darkgrey',
            text:
              member_type === 'Lifetime'
                ? 'N/A'
                : { Yes: 'Auto', No: 'Manual' }[auto_renew] || '-',
          },
        })
      );
    }
    if (
      frm.doc.__onload &&
      frm.doc.__onload['subscription_items'] &&
      frm.doc.__onload['subscription_items'].length > 0
    ) {
      frm.dashboard.add_section(
        frappe.render_template('gym_subscription_info', {
          sections: [
            {
              title: 'Subscriptions',
              items: frm.doc.__onload['subscription_items'].map(
                psd_customization.dashboard.make_subscription_info
              ),
            },
          ],
        })
      );
    }
  },

  add_actions: function(frm) {
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
