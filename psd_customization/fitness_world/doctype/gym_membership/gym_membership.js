// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gym Membership', {
  onload: function(frm) {
    frm.trigger('set_subscription_query');
  },
  refresh: function(frm) {
    frm.toggle_display(
      [
        'status',
        'validity_section',
        'start_date',
        'end_date',
        'frequency',
        'services_section',
        'items',
      ],
      frm.doc['docstatus'] === 1
    );
    frm.trigger('add_actions');
  },
  member: function(frm) {
    frm.trigger('set_subscription_query');
  },
  set_subscription_query: function(frm) {
    frm.toggle_display('subscription', frm.doc['member']);
    frm.set_query('subscription', () => ({
      filters: {
        reference_gym_member: frm.doc['member'],
        docstatus: 1,
      },
    }));
  },
  add_actions: async function(frm) {
    if (frm.doc.docstatus === 1) {
      frm.add_custom_button('Make Payment', async function() {
        frappe.model.open_mapped_doc({
          frm,
          method:
            'psd_customization.fitness_world.api.gym_membership.make_payment_entry',
        });
      });
    }
  },
});
