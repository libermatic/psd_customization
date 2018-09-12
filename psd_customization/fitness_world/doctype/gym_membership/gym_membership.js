// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gym Membership', {
  setup: function(frm) {
    if (frm.doc.docstatus !== 1) {
      frm.trigger('set_queries');
    }
  },
  refresh: function(frm) {
    frappe.ui.form.on('Gym Membership Item', {
      item_code: async function(frm, cdt, cdn) {
        const { item_code } = frappe.get_doc(cdt, cdn) || {};
        if (item_code) {
          const { message: price } = await frappe.call({
            method:
              'psd_customization.fitness_world.api.gym_membership.get_item_price',
            args: { item_code },
          });
          frappe.model.set_value(cdt, cdn, 'rate', price);
          frappe.model.set_value(cdt, cdn, 'qty', 1);
        } else {
          frappe.model.set_value(cdt, cdn, 'rate', 0);
        }
      },
      qty: function(frm, cdt, cdn) {
        const { qty = 0, rate = 0 } = frappe.get_doc(cdt, cdn) || {};
        frappe.model.set_value(cdt, cdn, 'amount', qty * rate);
      },
      rate: function(frm, cdt, cdn) {
        const { qty = 0, rate = 0 } = frappe.get_doc(cdt, cdn) || {};
        frappe.model.set_value(cdt, cdn, 'amount', qty * rate);
      },
      amount: function(frm) {
        frm.trigger('calculate_total');
      },
      items_remove: function(frm) {
        frm.trigger('calculate_total');
      },
    });
    frm.trigger('add_actions');
    frm.trigger('render_membership_details');
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
  calculate_total: function(frm) {
    const { items = [] } = frm.doc;
    frm.set_value(
      'total_amount',
      items.reduce((a, { amount: x = 0 }) => a + x, 0)
    );
  },
  add_actions: function(frm) {
    function get_status_props(status) {
      if (status === 'Active') {
        return {
          label: 'Stop Membership',
          method: 'psd_customization.fitness_world.api.gym_membership.stop',
        };
      }
      if (status === 'Stopped') {
        return {
          label: 'Resume Membership',
          method: 'psd_customization.fitness_world.api.gym_membership.resume',
        };
      }
      return null;
    }
    function get_repeat_props(auto_repeat) {
      return {
        label:
          auto_repeat === 'Yes' ? 'Disable Auto-Repeat' : 'Enable Auto-Repeat',
        method:
          'psd_customization.fitness_world.api.gym_membership.set_auto_repeat',
        args: { auto_repeat: auto_repeat === 'Yes' ? 'No' : 'Yes' },
      };
    }
    if (frm.doc.docstatus === 1) {
      frm
        .add_custom_button('Make Payment', function() {
          frappe.model.open_mapped_doc({
            frm,
            method:
              'psd_customization.fitness_world.api.gym_membership.make_payment_entry',
          });
        })
        .toggleClass(
          'btn-primary',
          frm.doc.__onload && !!frm.doc.__onload['unpaid_invoices']
        );
      const status_props = get_status_props(frm.doc['status']);
      if (status_props) {
        frm.add_custom_button(
          status_props.label,
          async function() {
            await frappe.call({
              method: status_props.method,
              args: { name: frm.doc['name'] },
            });
            frm.reload_doc();
          },
          'Manage'
        );
      }
      const repeat_props = get_repeat_props(frm.doc['auto_repeat']);
      frm.add_custom_button(
        repeat_props.label,
        async function() {
          await frappe.call({
            method: repeat_props.method,
            args: { name: frm.doc['name'], ...repeat_props.args },
          });
          frm.reload_doc();
        },
        'Manage'
      );
    }
  },
  render_membership_details: function(frm) {
    if (frm.doc.docstatus > 0 && frm.doc.__onload) {
      const {
        total_invoices,
        unpaid_invoices,
        outstanding,
        end_date,
      } = frm.doc.__onload;
      const { auto_repeat } = frm.doc;
      frm.dashboard.add_section(
        frappe.render_template('gym_membership_dashboard', {
          invoices: {
            color: unpaid_invoices ? 'orange' : 'green',
            total: total_invoices || '-',
            unpaid: unpaid_invoices || '-',
          },
          outstanding: {
            color: outstanding ? 'orange' : 'lightblue',
            amount: outstanding
              ? format_currency(
                  outstanding,
                  frappe.defaults.get_default('currency')
                )
              : '-',
          },
          validity: {
            color: moment().isSameOrBefore(end_date || undefined)
              ? 'lightblue'
              : 'red',
            end_date: end_date ? frappe.datetime.str_to_user(end_date) : '-',
          },
          repeat: {
            color: auto_repeat === 'Yes' ? 'lightblue' : 'darkgrey',
            text: { Yes: 'Auto', No: 'Manual' }[auto_repeat] || '-',
          },
        })
      );
    }
  },
});
