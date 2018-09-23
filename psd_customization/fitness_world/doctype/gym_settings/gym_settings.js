// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gym Settings', {
  setup: function(frm) {
    frm.trigger('set_queries');
  },
  set_queries: async function(frm) {
    ['sms_invoiced', 'sms_overdue', 'sms_receipt'].forEach(field => {
      frm.set_query(field, () => ({ filters: { type: 'Transactional' } }));
    });
  },
  refresh: async function(frm) {
    const { message: options } = await frappe.call({
      method: 'erpnext.accounts.doctype.pos_profile.pos_profile.get_series',
    });
    set_field_options('naming_series', options);
    frm.set_df_property('naming_series', 'hidden', 0);
  },
});
