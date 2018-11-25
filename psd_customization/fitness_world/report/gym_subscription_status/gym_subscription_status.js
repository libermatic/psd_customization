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
      fieldname: 'status',
      label: 'Status',
      fieldtype: 'Select',
      options: 'Active\nStopped\nExpired',
    },
  ],
};
