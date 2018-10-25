// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

/**
 * Parses serial numbers read by a qr code scanner and adds to serial_no field
 */

frappe.ui.form.on('Purchase Receipt', {
  setup: function(frm) {
    frm[
      'parse_serial_dialog'
    ] = psd_customization.ultimate_art.make_parse_serial_dialog();
  },
});

frappe.ui.form.on('Purchase Receipt Item', {
  parse_serial: psd_customization.ultimate_art.handle_parse_serial_dialog,
});

frappe.ui.form.on('Purchase Invoice', {
  setup: function(frm) {
    frm[
      'parse_serial_dialog'
    ] = psd_customization.ultimate_art.make_parse_serial_dialog();
  },
});

frappe.ui.form.on('Purchase Invoice Item', {
  parse_serial: psd_customization.ultimate_art.handle_parse_serial_dialog,
});
