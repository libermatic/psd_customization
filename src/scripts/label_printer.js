// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

function add_buttons(frm) {
  frm.add_custom_button('Clear', function() {
    ['company', 'price_list', 'print_dt', 'print_dn'].forEach(field =>
      frm.set_value(field, null)
    );
    frm.clear_table('items');
    frm.refresh_field('items');
  });
}

export const label_printer = {
  onload: function(frm) {
    frm.set_query('print_dt', {
      filters: [['name', 'in', 'Purchase Receipt, Purchase Invoice']],
    });
  },
  refresh: function(frm) {
    add_buttons(frm);
  },
  print_dn: async function(frm) {
    const { print_dt, print_dn, company, price_list } = frm.doc;
    if (print_dt && print_dn) {
      const { message: items } = await frappe.call({
        method: 'psd_customization.ultimate_art.api.label_printer.get_items',
        args: { print_dt, print_dn, company, price_list },
      });
      if (items) {
        const { grid } = frm.get_field('items');
        items.forEach(item => {
          const child_doc = Object.assign(
            frappe.model.add_child(frm.doc, 'Label Printer Item', 'items'),
            item
          );
        });
        frm.refresh_field('items');
      }
    }
  },
};

export default { label_printer };
