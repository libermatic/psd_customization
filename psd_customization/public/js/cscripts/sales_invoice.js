// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice', {
  setup: function(frm) {
    frm.subscription_selector = new psd.components.SubscriptionSelector();
  },
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
    const will_show = await frm.subscription_selector.register(frm, cdt, cdn);
    if (will_show) {
      frm.subscription_selector.show();
    }
  },
});
