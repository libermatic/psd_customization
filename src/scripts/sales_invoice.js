// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

import Vue from 'vue';

import CurrentSubscriptions from '../components/CurrentSubscriptions.vue';
import { month_diff_dec } from '../utils/datetime';

function has_gym_role() {
  return (
    frappe.user.has_role('Gym User') || frappe.user.has_role('Gym Manager')
  );
}

async function render_subscription_details(frm) {
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
    frm.susbcription_details = new Vue({
      el: node,
      render: h => h(CurrentSubscriptions, { props: { subscriptions } }),
    });
  }
}

export const sales_invoice = {
  setup: function(frm) {
    frm.toggle_display(['gym_member'], has_gym_role());
    if (has_gym_role()) {
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
    render_subscription_details(frm);
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
};

function get_description({
  item_name,
  gym_is_lifetime,
  gym_from_date,
  gym_to_date,
}) {
  if (gym_is_lifetime) {
    return `${item_name}: Lifetime validity, starting ${frappe.datetime.str_to_user(
      gym_from_date
    )}`;
  }
  return `${item_name}: Valid from ${frappe.datetime.str_to_user(
    gym_from_date
  )} to ${frappe.datetime.str_to_user(gym_to_date)}`;
}

function set_qty(frm, cdt, cdn) {
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
      gym_is_lifetime ? 60 : month_diff_dec(gym_from_date, gym_to_date)
    );
    frappe.model.set_value(
      cdt,
      cdn,
      'description',
      get_description({
        item_name,
        gym_from_date,
        gym_to_date,
        gym_is_lifetime,
      })
    );
  }
}

export const sales_invoice_item = {
  item_code: async function(frm, cdt, cdn) {
    if (has_gym_role()) {
      const { item_code } = frappe.get_doc(cdt, cdn);
      if (item_code) {
        const is_gym_subscription = await frappe.db.exists(
          'Gym Subscription Item',
          item_code
        );
        frappe.model.set_value(
          cdt,
          cdn,
          'is_gym_subscription',
          is_gym_subscription ? 1 : 0
        );
      } else {
        frappe.model.set_value(cdt, cdn, 'is_gym_subscription', 0);
      }
    }
  },
  is_gym_subscription: function(frm, cdt, cdn) {
    const { is_gym_subscription } = frappe.get_doc(cdt, cdn);
    if (is_gym_subscription) {
      const today = frappe.datetime.nowdate();
      frappe.model.set_value(cdt, cdn, 'gym_from_date', today);
      frappe.model.set_value(
        cdt,
        cdn,
        'gym_to_date',
        frappe.datetime.add_days(frappe.datetime.add_months(today, 1), -1)
      );
    } else {
      ['gym_from_date', 'gym_to_date', 'gym_is_lifetime'].forEach(field =>
        frappe.model.set_value(cdt, cdn, field, null)
      );
    }
  },
  gym_from_date: set_qty,
  gym_to_date: set_qty,
  gym_is_lifetime: async function(frm, cdt, cdn) {
    if (frm.doc.gym_is_lifetime) {
      await frappe.model.set_value(cdt, cdn, 'gym_to_date', null);
    }
    set_qty(frm, cdt, cdn);
  },
};

export default { sales_invoice, sales_invoice_item };
