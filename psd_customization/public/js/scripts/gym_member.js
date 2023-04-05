import MemberDashboard from '../components/MemberDashboard.vue';

function set_queries(frm) {
  ['notification_contact', 'emergency_contact'].forEach((contact) => {
    frm.set_query(contact, function (doc) {
      return {
        query:
          'psd_customization.fitness_world.api.gym_member.get_member_contacts',
        filters: { member: doc.name },
      };
    });
  });
}

function make_dialog(doctype) {
  return new frappe.ui.Dialog({
    title: `Select ${doctype}`,
    fields: [{ fieldname: 'docname', fieldtype: 'Link', options: doctype }],
    primary_action: async function () {
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

function render_address_and_contact(frm) {
  frappe.contacts.render_address_and_contact(frm);
  const address_dialog = make_dialog('Address');
  const $link_btn_address = $(
    '<button class="btn btn-xs btn-default btn-link-address">Link Address</button>'
  ).on('click', function () {
    address_dialog.show();
  });
  $(frm.fields_dict['address_html'].wrapper)
    .find('.btn-address')
    .after($link_btn_address);
  const contact_dialog = make_dialog('Contact');
  const $link_btn_contact = $(
    '<button class="btn btn-xs btn-default btn-link-contact">Link Contact</button>'
  ).on('click', function () {
    contact_dialog.show();
  });
  $(frm.fields_dict['contact_html'].wrapper)
    .find('.btn-contact')
    .unbind('click')
    .on('click', function () {
      frappe.new_doc('Contact');
    })
    .after($link_btn_contact);
}

function render_subscription_details(frm) {
  if (frm.doc.__onload) {
    const { subscriptions, last_trainer } = frm.doc.__onload;
    const { total_invoices, unpaid_invoices, outstanding } =
      frm.doc.__onload['subscription_details'] || {};
    const node = frm.dashboard.add_section('<div />').children()[0];
    new Vue({
      el: node,
      render: (h) =>
        h(MemberDashboard, {
          props: {
            total_invoices,
            unpaid_invoices,
            outstanding,
            subscriptions,
            last_trainer,
          },
        }),
    });
  }
}

function add_actions(frm) {
  frm.page
    .add_menu_item('Make Payment', function () {
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
  const trainable = (
    (frm.doc.__onload && frm.doc.__onload.subscriptions) ||
    []
  ).find(({ is_training }) => is_training);
  if (trainable) {
    frm.page.add_menu_item('Training Schedule', function () {
      frappe.set_route('training-schedule', {
        member: frm.doc.name,
        subscription: trainable.name,
      });
    });
  }
}

export const gym_member = {
  setup: function (frm) {
    set_queries(frm);
  },
  refresh: function (frm) {
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
    frm.toggle_display('member_id', frm.doc.__islocal);
    if (!frm.doc.__islocal) {
      render_address_and_contact(frm);
      render_subscription_details(frm);
      add_actions(frm);
    } else {
      frappe.contacts.clear_address_and_contact(frm);
    }
  },
  notification_contact: async function (frm) {
    const { notification_contact: contact } = frm.doc;
    if (contact) {
      const { message: notification_number } = await frappe.call({
        method:
          'psd_customization.fitness_world.api.gym_member.get_number_from_contact',
        args: { contact },
      });
      frm.set_value({ notification_number });
    } else {
      frm.set_value('notification_number', null);
    }
  },
};
