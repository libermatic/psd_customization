/**
 * Parses serial numbers read by a qr code scanner and adds to serial_no field
 */

import {
  make_parse_serial_dialog,
  handle_parse_serial_dialog,
} from '../ultimate_art';

const purchase_invoice_item = {
  parse_serial: handle_parse_serial_dialog,
};

export default {
  purchase_invoice_item,
  setup: function(frm) {
    frm['parse_serial_dialog'] = make_parse_serial_dialog();
  },
};
