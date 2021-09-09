// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

import BarcodeLabelDashboard from '../components/BarcodeLabelDashboard.vue';

export default {
  refresh: function(frm) {
    frm.trigger('add_menu_item');
    frm.trigger('render_barcode_details');
  },

  /**
   * Creates a EAN13 barcode by hashing item_code
   */
  add_menu_item: function(frm) {
    if (!frm.doc.__islocal) {
      function hash(str) {
        const hashint =
          str
            .split('')
            .reduce((a, x) => ((a << 5) - a + x.charCodeAt(0)) | 0, 0) >>> 0;
        const hashstr = hashint.toString();
        return `90${hashstr.slice(0, 10).padStart(10, '0')}`;
      }
      function checkdigit(code) {
        const mod = code
          .split('')
          .reverse()
          .reduce(
            (a, x, i) => (i % 2 ? parseInt(x) + a : parseInt(x) * 3 + a) % 10,
            0
          );
        return ((10 - mod) % 10).toString();
      }
      frm.page.add_menu_item('Generate New Barcode', async function() {
        const code = hash(frm.doc['item_code']);
        const check = checkdigit(code);
        await frm.add_child('barcodes', {
          barcode: code + check,
          barcode_type: 'EAN',
        });
        frm.refresh();
      });
    }
  },
  /**
   * Renders a barcode label in Dashboard with a button to Download as PNG
   */
  render_barcode_details: async function(frm) {
    if (!frm.doc.__islocal) {
      const { message: labels = [] } = await frappe.call({
        method: 'psd_customization.ultimate_art.api.item.get_label_data',
        args: { item_code: frm.doc['item_code'] },
      });
      if (labels.length > 0) {
        const $wrapper = frm.dashboard.add_section('<div />');
        frm.barcode_labels_vue = new Vue({
          data: { labels },
          el: $wrapper.html('<div />').children()[0],
          render: function(h) {
            return h(BarcodeLabelDashboard, { props: { labels: this.labels } });
          },
        });
      }
    }
  },
};
