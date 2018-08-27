// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gym Membership', {
  refresh: function(frm) {
    frm.trigger('set_defaults');
    frm.trigger('add_actions');
  },
  set_defaults: async function(frm) {
    const { message: settings = {} } = await frappe.db.get_value(
      'Gym Settings',
      null,
      'default_item_group'
    );
    if (settings['default_item_group']) {
      frm.set_query('item', 'items', () => ({
        filters: { item_group: settings['default_item_group'] },
      }));
    }
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
