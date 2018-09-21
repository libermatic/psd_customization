// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.listview_settings['Gym Member'] = {
  add_fields: ['status'],
  get_indicator: function({ status }) {
    if (status === 'Active') {
      return [status, 'green', 'status,=,Active'];
    }
    if (status === 'Stopped' || status === 'Expired') {
      return [status, 'red', `status,=,${status}`];
    }
  },
};
