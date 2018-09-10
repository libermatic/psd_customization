// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

/**
 * Sets query for Branch based on selected Company
 */

frappe.ui.form.on('Journal Entry', {
  refresh: function(frm) {
    frm.trigger('set_queries');
  },
  company: function(frm) {
    frm.trigger('set_queries');
  },
  set_queries: function(frm) {
    const { company } = frm.doc;
    frm.toggle_display('branch', !!company);
    frm.set_query('branch', () => ({ filters: { company } }));
  },
});
