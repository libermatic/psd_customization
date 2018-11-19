// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice', {
  setup: function(frm) {
    const has_gym_role =
      frappe.user.has_role('Gym User') || frappe.user.has_role('Gym Manager');
    frm.toggle_display(['gym_member'], has_gym_role);
    if (has_gym_role) {
      frm.get_field('items').grid.editable_fields = [
        { fieldname: 'item_code', columns: 3 },
        { fieldname: 'gym_from_date', columns: 2 },
        { fieldname: 'gym_to_date', columns: 2 },
        { fieldname: 'qty', columns: 1 },
        { fieldname: 'amount', columns: 2 },
      ];
      frm.get_field('items').grid.toggle_enable('qty', 0);
    }
  },
  gym_member: async function(frm) {
    frm.trigger('render_subscription_details');
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
  render_subscription_details: async function(frm) {
    if (frm.subscription_details) {
      frm.subscription_details.$destroy();
    }
    frm.fields_dict['gym_subscription_details_html'].$wrapper.empty();
    if (frm.doc['gym_member'] && frm.doc.__islocal) {
      const { message: subscriptions = [] } = await frappe.call({
        method:
          'psd_customization.fitness_world.api.gym_subscription.get_currents',
        args: { member: frm.doc['gym_member'] },
      });
      const node = frm.fields_dict['gym_subscription_details_html'].$wrapper
        .append('<div />')
        .children()[0];
      frm.susbcription_details = psd.make_subscription_details(node, {
        subscriptions,
      });
    }
  },
});

frappe.ui.form.on('Sales Invoice Item', {
  item_code: function(frm, cdt, cdn) {},
  gym_from_date: function(frm, cdt, cdn) {},
  gym_to_date: function(frm, cdt, cdn) {},
  set_qty: function(frm, cdt, cdn) {
    const {
      item_name,
      gym_from_date,
      gym_to_date,
      gym_is_lifetime,
    } = frappe.get_doc(cdt, cdn);
    if (gym_from_date && (gym_to_date || gym_is_lifetime)) {
      frappe.model.set_value(
        cdt,
        cdn,
        'qty',
        gym_is_lifetime
          ? 60
          : psd.utils.datetime.month_diff_dec(from_date, to_date)
      );
      frappe.model.set_value(
        cdt,
        cdn,
        'description',
        psd.utils.datetime.month_diff_dec({
          item_name,
          gym_from_date,
          gym_to_date,
          gym_is_lifetime,
        })
      );
    }
  },
});
