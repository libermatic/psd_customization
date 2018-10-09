// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

function _update_item_end_date(cdn) {
  const { qty, start_date } =
    frappe.get_doc('Gym Subscription Item', cdn) || {};
  if (qty && start_date) {
    frappe.model.set_value(
      'Gym Subscription Item',
      cdn,
      'end_date',
      frappe.datetime.add_days(frappe.datetime.add_months(start_date, qty), -1)
    );
  }
}

frappe.ui.form.on('Gym Subscription', {
  setup: function(frm) {
    if (frm.doc.docstatus !== 1) {
      frm.trigger('set_queries');
    }
  },
  set_queries: async function(frm) {
    const { message: settings = {} } = await frappe.db.get_value(
      'Gym Settings',
      null,
      'default_item_group'
    );
    if (settings['default_item_group']) {
      frm.set_query('item_code', 'items', () => ({
        filters: { item_group: settings['default_item_group'] },
      }));
    }
  },
  refresh: function(frm) {
    frappe.ui.form.on('Gym Subscription Item', {
      item_code: async function(frm, cdt, cdn) {
        const { item_code } = frappe.get_doc(cdt, cdn) || {};
        if (item_code) {
          const { message: start_date } = await frappe.call({
            method:
              'psd_customization.fitness_world.api.gym_subscription.get_next_from_date',
            args: { member: frm.doc['member'], item_code },
          });
          frappe.model.set_value(cdt, cdn, 'qty', 1);
          frappe.model.set_value(cdt, cdn, 'start_date', start_date);
        } else {
          frappe.model.set_value(cdt, cdn, 'qty', 0);
          frappe.model.set_value(cdt, cdn, 'start_date', null);
        }
      },
      qty: async function(frm, cdt, cdn) {
        const { item_code, qty = 0, rate = 0 } = frappe.get_doc(cdt, cdn) || {};
        if (qty) {
          const { member, posting_date: transaction_date } = frm.doc;
          const { message: price } = await frappe.call({
            method:
              'psd_customization.fitness_world.api.gym_subscription.get_item_price',
            args: {
              item_code,
              qty,
              member,
              transaction_date,
              no_pricing_rule: 0,
            },
          });
          frappe.model.set_value(cdt, cdn, 'rate', price);
        } else {
          frappe.model.set_value(cdt, cdn, 'rate', 0);
        }
        frappe.model.set_value(cdt, cdn, 'amount', qty * rate);
        _update_item_end_date(cdn);
      },
      rate: function(frm, cdt, cdn) {
        const { qty = 0, rate = 0 } = frappe.get_doc(cdt, cdn) || {};
        frappe.model.set_value(cdt, cdn, 'amount', qty * rate);
      },
      amount: function(frm) {
        frm.trigger('calculate_total');
      },
      start_date: function(frm, cdt, cdn) {
        _update_item_end_date(cdn);
      },
      items_remove: function(frm) {
        frm.trigger('calculate_total');
      },
    });
    frm.trigger('add_actions');
    frm.trigger('render_subscription_details');
  },
  member: async function(frm) {
    if (frm.doc['member']) {
      const { message: member } = await frappe.db.get_value(
        'Gym Member',
        frm.doc['member'],
        'subscription_plan'
      );
      frm.set_value('subscription_plan', member['subscription_plan']);
    }
  },
  subscription_plan: async function(frm) {
    if (frm.doc['subscription_plan'] && frm.doc['member']) {
      frm.clear_table('items');
      const {
        member,
        subscription_plan,
        posting_date: transaction_date,
      } = frm.doc;
      const { message: plan = [] } = await frappe.call({
        method:
          'psd_customization.fitness_world.api.gym_subscription.get_items',
        args: { member, subscription_plan, transaction_date },
      });
      plan.forEach(item => frm.add_child('items', item));
      frm.refresh_field('items');
    }
  },
  from_date: function(frm) {
    if (frm.doc['from_date'] && locals['Gym Subscription Item']) {
      Object.keys(locals['Gym Subscription Item']).forEach(cdn => {
        frappe.model.set_value(
          'Gym Subscription Item',
          cdn,
          'start_date',
          frm.doc['from_date']
        );
      });
    }
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
    if (frm.doc.__onload && frm.doc.docstatus === 1) {
      function get_color(status) {
        if (status === 'Paid') {
          return 'green';
        }
        if (status === 'Unpaid') {
          return 'orange';
        }
        if (status === 'Overdue') {
          return 'red';
        }
        return 'blue';
      }
      const { si_value, si_status } = frm.doc.__onload;
      const html = frappe.render_template('gym_subscription_dashboard', {
        amount: format_currency(
          si_value,
          frappe.defaults.get_default('currency')
        ),
        color: get_color(si_status),
      });
      frm.dashboard.show();
      frm.dashboard.add_section(html);
    }
  },
});
