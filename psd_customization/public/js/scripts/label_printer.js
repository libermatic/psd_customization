export function label_printer() {
  return {
    setup: function (frm) {
      frm.set_query('print_dt', () => ({
        filters: [['name', 'in', 'Purchase Receipt, Purchase Invoice']],
      }));
      frm.set_query('print_dn', ({ company }) => ({
        filters: { company },
      }));
      ['print_dt', 'print_dn'].forEach((field) => {
        frm.set_df_property(field, 'only_select', 1);
      });
      frm.set_query('batch_no', 'items', (_, cdt, cdn) => {
        const { item_code: item } = frappe.get_doc(cdt, cdn);
        return { filters: { item } };
      });
      frm.page.wrapper.on('view-change', () => {
        setup_buttons(frm);
      });
    },
    refresh: function (frm) {
      setup_buttons(frm);
    },
    print_dn: async function (frm) {
      const { print_dt, print_dn } = frm.doc;
      if (print_dt && print_dn) {
        await frappe.call({
          method: 'set_items_from_reference',
          doc: frm.doc,
          freeze: true,
        });
        frm.refresh_field('items');
      }
    },
  };
}

export function label_printer_item() {
  return {
    item_code: async function (frm, cdt, cdn) {
      const { item_code, batch_no } = frappe.get_doc(cdt, cdn) || {};
      const { price_list } = frm.doc;
      if (item_code && price_list) {
        const { message: details } = await frappe.call({
          method: 'psd_customization.ultimate_art.api.label_printer.get_item_details',
          args: { item_code, batch_no, price_list },
          error_handlers: { DoesNotExistError: () => {} },
        });
        ['price', 'barcode', 'barcode_type'].forEach((x) =>
          frappe.model.set_value(cdt, cdn, x, details[x])
        );
      } else {
        ['price', 'barcode', 'barcode_type'].forEach((x) =>
          frappe.model.set_value(cdt, cdn, x, null)
        );
      }
    },
  };
}

function setup_buttons(frm) {
  frm.disable_save();
  const is_print_preview = frm.page.current_view_name === 'print' || frm.hidden;

  frm.page.set_primary_action('Print', async function () {
    if (!is_print_preview) {
      let has_errored;
      await frm.save(undefined, undefined, undefined, () => {
        has_errored = true;
      });
      if (!has_errored) {
        frm.print_doc();
      }
    }
  });

  frm.page.set_secondary_action('Clear', async function () {
    ['print_dt', 'print_dn', 'skip'].forEach((field) =>
      frm.set_value(field, null)
    );
    frm.clear_table('items');
    frm.refresh_field('items');
  });
  frm.page.btn_secondary.toggle(!is_print_preview);
}
