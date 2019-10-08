// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

import CurrentSubscriptions from '../components/CurrentSubscriptions.vue';
import SubscriptionSelector from '../frappe-components/subscription-selector';
import { month_diff_dec } from '../utils/datetime';
import { set_naming_series } from '../utils/helpers';

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
    frm.subscription_details = new Vue({
      el: node,
      render: h => h(CurrentSubscriptions, { props: { subscriptions } }),
    });
  }
}

async function set_qty(frm, cdt, cdn) {
  const {
    item_code,
    gym_from_date,
    gym_to_date,
    gym_is_lifetime,
  } = frappe.get_doc(cdt, cdn);
  if (gym_is_lifetime) {
    const { message: sub_item = {} } = await frappe.db.get_value(
      'Gym Subscription Item',
      item_code,
      'quantity_for_lifetime'
    );
    frappe.model.set_value(
      cdt,
      cdn,
      'qty',
      sub_item.quantity_for_lifetime || 1
    );
  } else if (gym_from_date && gym_to_date) {
    frappe.model.set_value(
      cdt,
      cdn,
      'qty',
      month_diff_dec(gym_from_date, gym_to_date)
    );
  }
}

const sales_invoice_item = {
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
        frm.subscription_selector.register(frm, cdt, cdn);
      } else {
        frappe.model.set_value(cdt, cdn, 'is_gym_subscription', 0);
      }
    }
  },
  is_gym_subscription: async function(frm, cdt, cdn) {
    const { item_code, is_gym_subscription } = frappe.get_doc(cdt, cdn);
    const { gym_member: member } = frm.doc;
    if (is_gym_subscription && member) {
      const today = frappe.datetime.nowdate();
      await Promise.all([
        frappe.model.set_value(cdt, cdn, 'gym_from_date', today),
        frappe.model.set_value(
          cdt,
          cdn,
          'gym_to_date',
          frappe.datetime.add_days(frappe.datetime.add_months(today, 1), -1)
        ),
      ]);
      const [
        { message: subscription_item },
        { message: training = {} },
      ] = await Promise.all([
        frappe.call({
          method:
            'psd_customization.fitness_world.api.gym_subscription_item.get_subscription_item',
          args: { item_code },
        }),
        frappe.call({
          method:
            'psd_customization.fitness_world.api.trainer_allocation.get_last',
          args: { item_code, member },
        }),
      ]);
      if (subscription_item) {
        frm.subscription_selector.show({
          show_trainer: cint(subscription_item.requires_trainer),
          trainer: training.gym_trainer,
          slot: training.training_slot,
        });
      }
    } else {
      ['gym_from_date', 'gym_to_date', 'gym_is_lifetime'].forEach(field =>
        frappe.model.set_value(cdt, cdn, field, null)
      );
    }
  },
  gym_from_date: set_qty,
  gym_to_date: set_qty,
  gym_is_lifetime: async function(frm, cdt, cdn) {
    const { gym_is_lifetime } = frappe.get_doc(cdt, cdn);
    if (gym_is_lifetime) {
      await frappe.model.set_value(cdt, cdn, 'gym_to_date', null);
    }
    set_qty(frm, cdt, cdn);
  },
};

export default {
  sales_invoice_item,
  setup: function(frm) {
    if (has_gym_role()) {
      frm.get_field('items').grid.editable_fields = [
        { fieldname: 'item_code', columns: 3 },
        { fieldname: 'gym_from_date', columns: 2 },
        { fieldname: 'gym_to_date', columns: 2 },
        { fieldname: 'qty', columns: 1 },
        { fieldname: 'amount', columns: 2 },
      ];
      frm.get_field('items').grid.toggle_enable('qty', 0);
      frm.subscription_selector = new SubscriptionSelector();
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
  company: set_naming_series,
};
