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

export default {
  month_diff_dec,
};
