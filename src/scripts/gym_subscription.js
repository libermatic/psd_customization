// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

import Vue from 'vue';

import SubscriptionDashboard from '../components/SubscriptionDashboard.vue';

function set_dates(frm) {
  const from_date = frappe.datetime.get_today();
  const to_date = frappe.datetime.add_days(
    frappe.datetime.add_months(from_date, 1),
    -1
  );
  frm.set_value('from_date', from_date);
  frm.set_value('to_date', to_date);
}
function add_actions(frm) {
  if (frm.doc.docstatus === 1) {
    function get_invoice_props() {
      if (frm.doc['reference_invoice']) {
        return {
          label: 'Make Payment',
          method:
            'psd_customization.fitness_world.api.gym_subscription.make_payment_entry',
        };
      }
      return {
        label: 'Make Invoice',
        method:
          'psd_customization.fitness_world.api.gym_subscription.make_sales_invoice',
      };
    }
    function get_button_state() {
      const { is_opening, reference_invoice, __onload } = frm.doc;
      if (is_opening) {
        return true;
      }
      if (
        reference_invoice &&
        __onload &&
        __onload.invoice &&
        __onload.invoice.status === 'Paid'
      ) {
        return true;
      }
      return false;
    }
    const { label, method } = get_invoice_props();
    frm
      .add_custom_button(label, function() {
        frappe.model.open_mapped_doc({ frm, method });
      })
      .addClass('btn-primary')
      .toggleClass('disabled', get_button_state());
  }
}
function render_subscription_details(frm) {
  if (frm.doc.__onload) {
    const { invoice } = frm.doc.__onload;
    const node = frm.dashboard.add_section('<div />').children()[0];
    frm.dashboard.show();
    new Vue({
      el: node,
      render: h => h(SubscriptionDashboard, { props: { invoice } }),
    });
  }
}

export const gym_subscription = {
  refresh: function(frm) {
    if (frm.doc.__islocal && frm.doc['amended_from']) {
      frm.set_value('reference_invoice', null);
    }
    if (frm.doc.__islocal) {
      set_dates(frm);
    }
    add_actions(frm);
    render_subscription_details(frm);
  },
  subscription_item: function(frm) {
    if (!frm.doc['subscription_item']) {
      frm.set_value('subscription_name', null);
    }
  },
};

export default { gym_subscription };
