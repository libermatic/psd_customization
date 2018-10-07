// Copyright (c) 2016, Libermatic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Gym Membership Status'] = {
  filters: [
    {
      fieldname: 'member',
      label: 'Member',
      fieldtype: 'Link',
      options: 'Gym Member',
    },
    {
      fieldname: 'member_status',
      label: 'Member Activity',
      fieldtype: 'Select',
      options: '\nActive\nStopped',
    },
    {
      fieldname: 'membership_item',
      label: 'Membership Item',
      fieldtype: 'Link',
      options: 'Item',
      get_query: function() {
        let item_group = null;
        frappe.call({
          method: 'frappe.client.get_value',
          args: { doctype: 'Gym Settings', fieldname: 'default_item_group' },
          async: false,
          callback: function({ message = {} }) {
            item_group = message['default_item_group'];
          },
        });
        return { doctype: 'Item', filters: { item_group } };
      },
    },
    {
      fieldname: 'membership_status',
      label: 'Invoice Status',
      fieldtype: 'Select',
      options: '\nPaid\nUnpaid',
    },
  ],
};
