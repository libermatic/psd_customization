// Copyright (c) 2016, Libermatic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Gym Subscription Status'] = {
  filters: [
    {
      fieldname: 'member',
      label: 'Member',
      fieldtype: 'Link',
      options: 'Gym Member',
    },
    {
      fieldname: 'subscription_item',
      label: 'Subscription Item',
      fieldtype: 'Link',
      options: 'Gym Subscription Item',
    },
    {
      fieldname: 'between_dates',
      label: 'Between Dates',
      fieldtype: 'DateRange',
      default: [
        frappe.datetime.add_months(frappe.datetime.month_start(), -1),
        frappe.datetime.month_end(),
      ],
    },
    {
      fieldname: 'status',
      label: 'Status',
      fieldtype: 'Select',
      options: '\nActive\nStopped\nExpired',
    },
  ],
};
