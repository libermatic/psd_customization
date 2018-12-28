// Copyright (c) 2016, Libermatic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Gym Trainer Allotment'] = {
  filters: [
    {
      fieldname: 'gym_trainer',
      label: 'Trainer',
      fieldtype: 'Link',
      options: 'Gym Trainer',
    },
    {
      fieldname: 'training_slot',
      label: 'Slot',
      fieldtype: 'Link',
      options: 'Training Slot',
    },
    {
      fieldname: 'from_date',
      label: 'From',
      fieldtype: 'Date',
      default: frappe.datetime.month_start(),
    },
    {
      fieldname: 'to_date',
      label: 'To',
      fieldtype: 'Date',
      default: frappe.datetime.month_end(),
    },
  ],
};
