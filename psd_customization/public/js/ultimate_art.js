// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.provide('psd_customization');
frappe.provide('psd_customization.ultimate_art');

psd_customization.ultimate_art.make_parse_serial_dialog = function() {
  return new frappe.ui.Dialog({
    title: 'Parse Serial',
    fields: [{ fieldname: 'raw_text', label: 'Raw Text', fieldtype: 'Code' }],
  });
};

/**
 * Read raw_text and set serial_no on child table
 * format:
 *   "CTNSN":"3211503003308","unitSN":["3211506030507","3211515030503",
 *   "3211543030504","3211570030505","3211588030506"]
 */
psd_customization.ultimate_art.handle_parse_serial_dialog = function(
  frm,
  cdt,
  cdn
) {
  const { parse_serial_dialog: dialog } = frm;
  dialog.set_primary_action('Parse', function() {
    const { serial_no: prev_serial_no = '' } = locals[cdt][cdn];
    try {
      const serials = dialog
        .get_value('raw_text')
        .split('\n')
        .reduce(
          (acc, raw) =>
            raw ? acc.concat(JSON.parse(`{${raw}}`)['unitSN']) : acc,
          prev_serial_no.split('\n')
        );
      frappe.model.set_value(cdt, cdn, 'serial_no', `${serials.join('\n')}`);
    } catch {
      console.warn('Invalid serial format detected: serial_no not set');
    }
    dialog.hide();
    dialog.get_primary_btn().unbind();
  });
  dialog.show();
};
