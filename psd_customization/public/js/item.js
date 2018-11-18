// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item', {
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
        await frm.set_value('barcode', code + check);
      });
    }
  },
  /**
   * Renders a barcode label in Dashboard with a button to Download as PNG
   */
  render_barcode_details: async function(frm) {
    if (!frm.doc.__islocal) {
      const { message: label_data = {} } = await frappe.call({
        method: 'psd_customization.ultimate_art.api.item.get_label_data',
        args: { item_code: frm.doc['item_code'] },
      });
      if (label_data.barcode) {
        const dashboard_section = frm.dashboard.add_section(
          frappe.render_template('barcode_label', { doc: label_data })
        );
        const barcode_area = frm.dashboard.wrapper.find('.psd-barcode-area');
        frappe.require('assets/frappe/js/lib/JsBarcode.all.min.js', function() {
          try {
            barcode_area.html('<svg />');
            JsBarcode(barcode_area.find('svg')[0], label_data.barcode, {
              format: 'ean13',
              margin: 0,
              marginTop: 4,
              marginBottom: 4,
              height: 40,
              width: 2,
              fontSize: 11,
              flat: true,
            });
            frappe.require(
              'assets/psd_customization/js/lib/dom-to-image.min.js',
              function() {
                const node = frm.dashboard.wrapper.find('#barcode-label')[0];
                async function download_label() {
                  try {
                    const dataUrl = await domtoimage.toPng(node);
                    $('<a />')
                      .attr({
                        href: dataUrl,
                        download: `${label_data.item_code} - ${
                          label_data.barcode
                        }.png`,
                      })[0]
                      .click();
                  } catch (e) {
                    console.error('oops, something went wrong!', e);
                  }
                }
                $(dashboard_section)
                  .find('.download_image')
                  .click(download_label);
              }
            );
          } catch (e) {
            barcode_area.text('INVALID');
            $(dashboard_section)
              .find('.download_image')
              .addClass('disabled');
          }
        });
      }
    }
  },
});
