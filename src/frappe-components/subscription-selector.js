// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

import Vue from 'vue';
import CurrentSubscriptions from '../components/CurrentSubscriptions.vue';
import { month_diff_dec } from '../utils/datetime';

function get_to_date(date, freq) {
  return frappe.datetime.add_days(frappe.datetime.add_months(date, freq), -1);
}

export default class SubscriptionSelector {
  constructor() {
    const today = frappe.datetime.nowdate();
    this.dialog = new frappe.ui.Dialog({
      title: 'Select Subscription Period',
      fields: [
        {
          label: 'Frequency',
          fieldname: 'frequency',
          fieldtype: 'Select',
          options: 'Monthly\nQuarterly\nHalf-Yearly\nYearly\nLifetime',
          default: 'Monthly',
        },
        {
          label: 'Trainer',
          fieldname: 'trainer',
          fieldtype: 'Link',
          options: 'Gym Trainer',
        },
        {
          label: 'Slot',
          fieldname: 'slot',
          fieldtype: 'Link',
          options: 'Training Slot',
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
  async register(frm, cdt, cdn) {
    const row = frappe.get_doc(cdt, cdn) || {};
    if (!row.item_code) {
      return false;
    }
    this.dialog.get_primary_btn().off('click');
    this.dialog.set_primary_action('OK', () => {
      const {
        frequency,
        from_date,
        to_date,
        trainer,
        slot,
      } = this.dialog.get_values();
      frappe.model.set_value(
        cdt,
        cdn,
        'qty',
        frequency === 'Lifetime' ? 60 : month_diff_dec(from_date, to_date)
      );
      if (frequency === 'Lifetime') {
        frappe.model.set_value(cdt, cdn, 'gym_is_lifetime', 1);
        frappe.model.set_value(cdt, cdn, 'gym_from_date', from_date);
      } else {
        frappe.model.set_value(cdt, cdn, 'gym_from_date', from_date);
        frappe.model.set_value(cdt, cdn, 'gym_to_date', to_date);
      }
      frappe.model.set_value(cdt, cdn, 'gym_trainer', trainer);
      frappe.model.set_value(cdt, cdn, 'gym_training_slot', slot);
      this.dialog.hide();
    });
    return true;
  }
  show({ show_trainer } = {}) {
    ['trainer', 'slot'].forEach(field => {
      this.dialog.fields_dict[field].toggle(show_trainer);
    });
    this.dialog.show();
  }
}
