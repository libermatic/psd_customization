// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

export function month_diff_dec(d1, d2) {
  const last_start = frappe.datetime.add_days(d2, 1);
  let next_start = d1;
  let cur_start = d1;
  let months = 0;
  let cur_months = 0;
  while (moment(next_start).isSameOrBefore(last_start)) {
    cur_start = next_start;
    cur_months = months;
    next_start = frappe.datetime.add_months(next_start, 1);
    months += 1;
  }
  const rem_days = frappe.datetime.get_day_diff(last_start, cur_start);
  const days_in_month = frappe.datetime.get_day_diff(next_start, cur_start);
  return cur_months + rem_days / days_in_month;
}

/**
 * Sets naming_series of the DocType based on Company abbr.
 * This happens only when naming_series for the applicable DocTypes are set as
 * per the schema below.
 */

export async function set_naming_series(frm, dt) {
  const { message: company } = await frappe.db.get_value(
    'Company',
    frm.doc['company'],
    'abbr'
  );
  const renaming_doctypes = {
    'Sales Invoice': `SI-${company['abbr']}/.YY.-`,
    'Payment Entry': `PE-${company['abbr']}/.YY.-`,
    'Journal Entry': `JV-${company['abbr']}/.YY.-`,
  };
  const naming_series = frm.get_docfield('naming_series').options;
  if (naming_series.indexOf(renaming_doctypes[dt]) > -1) {
    frm.set_value('naming_series', renaming_doctypes[dt]);
  } else {
    frm.set_value('naming_series', naming_series.split('\n')[0]);
  }
}
