// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Batch Item Expiry Valuation'] = {
  filters: [
    {
      fieldname: 'from_date',
      label: __('From Date'),
      fieldtype: 'Date',
      width: '80',
      default: frappe.sys_defaults.year_start_date,
      reqd: 1,
    },
    {
      fieldname: 'to_date',
      label: __('To Date'),
      fieldtype: 'Date',
      width: '80',
      default: frappe.datetime.get_today(),
      reqd: 1,
    },
    {
      fieldname: 'warehouse',
      label: __('Warehouse'),
      fieldtype: 'Link',
      options: 'Warehouse',
      width: '80',
    },
    {
      fieldname: 'price_list',
      label: __('Price List'),
      fieldtype: 'Link',
      options: 'Price List',
      width: '80',
      default: 'Standard Selling',
    },
    {
      fieldname: 'days_to_expiry',
      label: 'Days to Expiry',
      fieldtype: 'Select',
      options: '\n30\n60\n90\n120\n150',
      width: '80',
    },
  ],
};
