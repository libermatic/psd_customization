// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gym Fee', {
  setup: function(frm) {
    frm.set_query('membership', () => ({
      filters: { docstatus: 1 },
    }));
    frappe.ui.form.on('Gym Membership Item', {
      item_code: async function(frm, cdt, cdn) {
        const { item_code } = frappe.get_doc(cdt, cdn) || {};
        if (item_code) {
          const { message: price } = await frappe.call({
            method:
              'psd_customization.fitness_world.api.gym_membership.get_item_price',
            args: { item_code },
          });
          frappe.model.set_value(cdt, cdn, 'rate', price);
          frappe.model.set_value(cdt, cdn, 'qty', 1);
        } else {
          frappe.model.set_value(cdt, cdn, 'rate', 0);
        }
      },
      qty: function(frm, cdt, cdn) {
        const { qty = 0, rate = 0 } = frappe.get_doc(cdt, cdn) || {};
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
  refresh: function(frm) {
    frm.trigger('add_actions');
  },
  membership: async function(frm) {
    const { membership } = frm.doc;
    if (membership) {
      const { message: from_date } = await frappe.call({
        method:
          'psd_customization.fitness_world.api.gym_fee.get_next_from_date',
        args: { membership },
      });
      frm.set_value('from_date', from_date);
      frm.set_value('duration', 1);
    }
  },
  from_date: function(frm) {
    frm.trigger('set_to_date');
  },
  duration: async function(frm) {
    frm.trigger('set_to_date');
    await frm.trigger('set_items');
    frm.trigger('calculate_total');
  },
  set_to_date: async function(frm) {
    const { membership, from_date, duration } = frm.doc;
    if (from_date && duration) {
      const { message: to_date } = await frappe.call({
        method: 'psd_customization.fitness_world.api.gym_fee.get_to_date',
        args: { membership, from_date, duration },
      });
      frm.set_value('to_date', to_date);
    }
  },
  set_items: async function(frm) {
    frm.clear_table('items');
    const { membership, duration } = frm.doc;
    const { message: items } = await frappe.call({
      method: 'psd_customization.fitness_world.api.gym_fee.get_items',
      args: { membership, duration },
    });
    items.forEach(item => frm.add_child('items', item));
    frm.refresh_field('items');
  },
  calculate_total: function(frm) {
    const { items = [] } = frm.doc;
    frm.set_value(
      'total_amount',
      items.reduce((a, { amount: x = 0 }) => a + x, 0)
    );
  },
  add_actions: function(frm) {
    if (frm.doc.docstatus === 1) {
      frm.add_custom_button('Make Payment', async function() {
        frappe.model.open_mapped_doc({
          frm,
          method:
          'psd_customization.fitness_world.api.gym_fee.make_payment_entry',
        });
      });
    }
  },
});
