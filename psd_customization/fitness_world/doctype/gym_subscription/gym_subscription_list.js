// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.listview_settings['Gym Subscription'] = {
  add_fields: ['status', 'to_date'],
  get_indicator: function({ status, to_date }) {
    if (status === 'Paid') {
      return [status, 'green', 'status,=,Paid'];
    }
    if (status === 'Unpaid') {
      if (moment().isAfter(to_date)) {
        return ['Overdue', 'red', 'status,=,Unpaid|to_date,<=,Today'];
      }
      return [status, 'orange', 'status,=,Unpaid|to_date,>,Today'];
    }
  },
};
