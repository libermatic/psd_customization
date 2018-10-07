// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

function _update_item_end_date(cdn) {
  const { qty, start_date } = frappe.get_doc('Gym Membership Item', cdn) || {};
  if (qty && start_date) {
    frappe.model.set_value(
      'Gym Membership Item',
      cdn,
      'end_date',
      frappe.datetime.add_days(frappe.datetime.add_months(start_date, qty), -1)
    );
  }
}

frappe.ui.form.on('Gym Membership', {
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
    frappe.ui.form.on('Gym Membership Item', {
      item_code: async function(frm, cdt, cdn) {
        const { member, posting_date: transaction_date } = frm.doc;
        const { item_code } = frappe.get_doc(cdt, cdn) || {};
        if (item_code) {
          const { message: price } = await frappe.call({
            method:
              'psd_customization.fitness_world.api.gym_membership.get_item_price',
            args: { item_code, member, transaction_date, no_pricing_rule: 0 },
          });
          frappe.model.set_value(cdt, cdn, 'rate', price);
          frappe.model.set_value(cdt, cdn, 'qty', 1);
        } else {
          frappe.model.set_value(cdt, cdn, 'rate', 0);
        }
      },
      qty: function(frm, cdt, cdn) {
        const { qty = 0, rate = 0, start_date } =
          frappe.get_doc(cdt, cdn) || {};
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
    frm.trigger('render_membership_details');
  },
  member: async function(frm) {
    if (frm.doc['member']) {
      const [{ message: member }, { message: from_date }] = await Promise.all([
        frappe.db.get_value('Gym Member', frm.doc['member'], 'membership_plan'),
        frappe.call({
          method:
            'psd_customization.fitness_world.api.gym_membership.get_next_from_date',
          args: { member: frm.doc['member'] },
        }),
      ]);
      frm.set_value('membership_plan', member['membership_plan']);
      frm.set_value('from_date', from_date || frappe.datetime.get_today());
    }
  },
  membership_plan: async function(frm) {
    if (frm.doc['membership_plan'] && frm.doc['member']) {
      frm.clear_table('items');
      const {
        member,
        membership_plan,
        posting_date: transaction_date,
      } = frm.doc;
      const { message: plan = [] } = await frappe.call({
        method: 'psd_customization.fitness_world.api.gym_membership.get_items',
        args: { member, membership_plan, transaction_date },
      });
      plan.forEach(item => frm.add_child('items', item));
      frm.refresh_field('items');
    }
  },
  from_date: function(frm) {
    if (frm.doc['from_date'] && locals['Gym Membership Item']) {
      Object.keys(locals['Gym Membership Item']).forEach(cdn => {
        frappe.model.set_value(
          'Gym Membership Item',
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
              'psd_customization.fitness_world.api.gym_membership.make_payment_entry',
          };
        }
        return {
          label: 'Make Invoice',
          method:
            'psd_customization.fitness_world.api.gym_membership.make_sales_invoice',
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
  render_membership_details: function(frm) {
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
      const html = frappe.render_template('gym_membership_dashboard', {
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
