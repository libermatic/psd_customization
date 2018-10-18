// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.listview_settings['Gym Membership'] = {
  add_fields: ['status', 'end_date'],
  get_indicator: function({ status, end_date }) {
    if (status === 'Stopped') {
      return [status, 'orange', 'status,=,Stopped'];
    }
    if (status === 'Active') {
      return [status, 'green', 'status,=,Active'];
    }
    if (moment().isAfter(end_date)) {
      return ['Expired', 'red', 'end_date,<,Today'];
    }
    return [
      'Inactive',
      'darkgrey',
      'status,not in,Active,Stopped|end_date,>=,Today',
    ];
  },
};
