// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

/**
 * Enables and sets query for gym_parent_items based default_item_group set in
 * Gym Settings
 */

frappe.ui.form.on('Item', {
  refresh: function(frm) {
    frm.trigger('enable_fields');
  },
  item_group: function(frm) {
    frm.trigger('enable_fields');
  },
  enable_fields: async function(frm) {
    const { message: settings = {} } = await frappe.db.get_value(
      'Gym Settings',
      null,
      'default_item_group'
    );
    frm.toggle_display(
      ['gym_section', 'is_base_gym_membership_item', 'gym_parent_items'],
      settings['default_item_group'] === frm.doc['item_group']
    );
    if (settings['default_item_group']) {
      frm.set_query('item', 'gym_parent_items', {
        filters: { item_group: settings['default_item_group'] },
      });
    }
  },
});
