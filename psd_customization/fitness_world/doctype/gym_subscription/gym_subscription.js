// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gym Subscription', {
  refresh: function(frm) {
    if (frm.doc.__islocal && frm.doc['amended_from']) {
      frm.set_value('reference_invoice', null);
      frm.set_value('status', null);
    }
    if (frm.doc.__islocal) {
      frm.trigger('set_dates');
    }
    frm.trigger('add_actions');
    frm.trigger('render_subscription_details');
  },
  subscription_item: function(frm) {
    if (!frm.doc['subscription_item']) {
      frm.set_value('subscription_name', null);
    }
  },
  set_dates: function(frm) {
    const from_date = frappe.datetime.get_today();
    const to_date = frappe.datetime.add_days(
      frappe.datetime.add_months(from_date, 1),
      -1
    );
    frm.set_value('from_date', from_date);
    frm.set_value('to_date', to_date);
  },
  add_actions: function(frm) {
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
      const { label, method } = get_invoice_props();
      frm
        .add_custom_button(label, function() {
          frappe.model.open_mapped_doc({ frm, method });
        })
        .addClass('btn-primary')
        .toggleClass('disabled', frm.doc['status'] === 'Paid');
    }
  },
  render_subscription_details: function(frm) {
    if (frm.doc.__onload) {
      const { invoice } = frm.doc.__onload;
      const node = frm.dashboard.add_section('<div />').children()[0];
      frm.dashboard.show();
      psd.make_subscription_dashboard(node, { invoice });
    }
  },
});
