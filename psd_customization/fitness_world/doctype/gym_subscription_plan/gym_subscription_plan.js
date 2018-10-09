// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gym Subscription Plan', {
  setup: function(frm) {
    frm.trigger('set_queries');
  },
  refresh: function(frm) {
    frappe.ui.form.on('Gym Subscription Item', {
      item_code: async function(frm, cdt, cdn) {
        const { item_code } = frappe.get_doc(cdt, cdn) || {};
        if (item_code) {
          frappe.model.set_value(cdt, cdn, 'qty', 1);
        } else {
          frappe.model.set_value(cdt, cdn, 'qty', 0);
        }
      },
      qty: async function(frm, cdt, cdn) {
        const { item_code, qty = 0, rate = 0 } = frappe.get_doc(cdt, cdn) || {};
        if (qty) {
          const { item_code } = frappe.get_doc(cdt, cdn) || {};
          const { message: price } = await frappe.call({
            method:
              'psd_customization.fitness_world.api.gym_subscription.get_item_price',
            args: { item_code, qty, no_pricing_rule: 0 },
          });
          frappe.model.set_value(cdt, cdn, 'rate', price);
        } else {
          frappe.model.set_value(cdt, cdn, 'rate', 0);
        }
        frappe.model.set_value(cdt, cdn, 'amount', qty * rate);
      },
      rate: function(frm, cdt, cdn) {
        const { qty = 0, rate = 0 } = frappe.get_doc(cdt, cdn) || {};
        frappe.model.set_value(cdt, cdn, 'amount', qty * rate);
      },
      amount: function(frm) {
        frm.trigger('calculate_total');
      },
      items_remove: function(frm) {
        frm.trigger('calculate_total');
      },
    });
  },
  set_queries: async function(frm) {
    const { message: settings = {} } = await frappe.db.get_value(
      'Gym Settings',
      null,
      'default_item_group'
    );
    if (settings['default_item_group']) {
      frm.set_query('item_code', 'items', () => ({
        filters: { item_group: settings['default_item_group'] },
      }));
    }
  },
  calculate_total: function(frm) {
    const { items = [] } = frm.doc;
    frm.set_value(
      'total_amount',
      items.reduce((a, { amount: x = 0 }) => a + x, 0)
    );
  },
});
