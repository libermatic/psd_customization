// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

/**
 * Sets naming_series of the DocType based on Company abbr.
 * This happens only when naming_series for the applicable DocTypes are set as
 * per the schema below.
 */

async function set_naming_series(frm, dt) {
  const { message: company } = await frappe.db.get_value(
    'Company',
    frm.doc['company'],
    'abbr'
  );
  const renaming_doctypes = {
    'Sales Invoice': `SI-${company['abbr']}/.YY.-`,
    'Payment Entry': `PE-${company['abbr']}/.YY.-`,
  };
  const naming_series = frm.get_docfield('naming_series').options;
  if (naming_series.indexOf(renaming_doctypes[dt]) > -1) {
    frm.set_value('naming_series', renaming_doctypes[dt]);
  }
}

frappe.ui.form.on('Sales Invoice', { company: set_naming_series });
frappe.ui.form.on('Payment Entry', { company: set_naming_series });
