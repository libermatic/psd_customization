// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

import Vue from 'vue';

import CurrentSubscriptions from '../components/CurrentSubscriptions.vue';
import { month_diff_dec } from '../utils/datetime';

function get_to_date(date, freq) {
  return frappe.datetime.add_days(frappe.datetime.add_months(date, freq), -1);
}

function get_description({ item_name, frequency, from_date, to_date }) {
  if (frequency === 'Lifetime') {
    return `${item_name}: Lifetime validity, starting ${frappe.datetime.str_to_user(
      from_date
    )}`;
  }
  return `${item_name}: Valid from ${frappe.datetime.str_to_user(
    from_date
  )} to ${frappe.datetime.str_to_user(to_date)}`;
}

export default class SubscriptionDialog {
  constructor() {
    const today = frappe.datetime.nowdate();
    this.dialog = new frappe.ui.Dialog({
      title: 'Select Subscription Period',
      fields: [
        { fieldname: 'ht', fieldtype: 'HTML' },
        { fieldtype: 'Section Break' },
        {
          label: 'Frequency',
          fieldname: 'frequency',
          fieldtype: 'Select',
          options: 'Monthly\nQuarterly\nHalf-Yearly\nYearly\nLifetime',
          default: 'Monthly',
        },
        { fieldtype: 'Column Break' },
        {
          label: 'From Date',
          fieldname: 'from_date',
          fieldtype: 'Date',
          default: today,
        },
        {
          label: 'To Date',
          fieldname: 'to_date',
          fieldtype: 'Date',
          default: get_to_date(today, 1),
        },
      ],
    });
    this._setup();
  }
  _setup() {
    const months = {
      Monthly: 1,
      Quarterly: 3,
      'Half-Yearly': 6,
      Yearly: 12,
      Lifetime: 60,
    };
    const handle_to_date = () => {
      const { frequency, from_date } = this.dialog.get_values();
      if (from_date && frequency && months[frequency]) {
        if (frequency === 'Lifetime') {
          this.dialog.set_value('to_date', null);
          this.dialog.fields_dict['to_date'].toggle(false);
        } else {
          this.dialog.fields_dict['to_date'].toggle(true);
          this.dialog.set_value(
            'to_date',
            get_to_date(from_date, months[frequency])
          );
        }
      }
    };
    this.dialog.fields_dict['frequency'].$input.on('input', handle_to_date);
    this.dialog.fields_dict['from_date'].$input.on('blur', handle_to_date);
  }
  async load_priors(member) {
    if (this.vm) {
      this.vm.$destroy();
    }
    this.dialog.fields_dict['ht'].$wrapper.empty();
    const { message: subscriptions = [] } = await frappe.call({
      method:
        'psd_customization.fitness_world.api.gym_subscription.get_currents',
      args: { member },
    });

    this.vm = new Vue({
      el: $('<div />').appendTo(this.dialog.fields_dict['ht'].$wrapper)[0],
      render: h => h(CurrentSubscriptions, { props: { subscriptions } }),
    });
  }
  async register(frm, cdt, cdn) {
    const row = frappe.get_doc(cdt, cdn) || {};
    if (!row.item_code) {
      return false;
    }
    const { message: sub_item } = await frappe.call({
      method:
        'psd_customization.fitness_world.api.gym_subscription_item.get_subscription_item',
      args: { item_code: row.item_code },
    });
    if (!sub_item) {
      return false;
    }
    const { item_name } = sub_item;
    if (item_name) {
      this.dialog.set_title(`Select Period for ${item_name}`);
    }
    this.dialog.set_primary_action('OK', () => {
      const { frequency, from_date, to_date } = this.dialog.get_values();
      frappe.model.set_value(
        cdt,
        cdn,
        'qty',
        frequency === 'Lifetime' ? 60 : month_diff_dec(from_date, to_date)
      );
      frappe.model.set_value(
        cdt,
        cdn,
        'description',
        get_description({
          frequency,
          from_date,
          to_date,
          item_name: item_name || row.item_name,
        })
      );
      frappe.model.set_value(cdt, cdn, 'is_gym_subscription', 1);
      if (frequency === 'Lifetime') {
        frappe.model.set_value(cdt, cdn, 'gym_is_lifetime', 1);
        frappe.model.set_value(cdt, cdn, 'gym_from_date', from_date);
      } else {
        frappe.model.set_value(cdt, cdn, 'gym_from_date', from_date);
        frappe.model.set_value(cdt, cdn, 'gym_to_date', to_date);
      }
      this.dialog.hide();
      this.dialog.get_primary_btn().off('click');
    });
    return true;
  }
  show() {
    this.dialog.show();
  }
}
