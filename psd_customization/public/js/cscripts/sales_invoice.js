// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice', {
  gym_member: async function(frm) {
    const { gym_member } = frm.doc;
    if (gym_member) {
      const { message: doc = {} } = await frappe.db.get_value(
        'Gym Member',
        gym_member,
        'customer'
      );
      frm.set_value('customer', doc['customer']);
    } else {
      frm.set_value('gym_member_name', null);
      frm.set_value('customer', null);
    }
  },
});

frappe.ui.form.on('Sales Invoice Item', {
  item_code: async function(frm, cdt, cdn) {
    const { item_code } = frappe.get_doc(cdt, cdn) || {};
    if (item_code) {
      const { message } = await frappe.call({
        method:
          'psd_customization.fitness_world.api.gym_subscription_item.get_subscription_item',
        args: { item_code },
      });
      console.log(message);
    }
    console.log(cdn, cdt);
    console.log(item_code);
    console.log('ljk');
    // if (item_code) {
    //   const { from_date, to_date } = frm.doc;
    //   if (parentfield === 'service_items' && from_date && to_date) {
    //     frappe.model.set_value(
    //       cdt,
    //       cdn,
    //       'qty',
    //       psd_customization.utils.month_diff_dec(from_date, to_date)
    //     );
    //   } else {
    //     frappe.model.set_value(cdt, cdn, 'qty', 1);
    //   }
    // } else {
    //   frappe.model.set_value(cdt, cdn, 'qty', 0);
    // }
  },
});
