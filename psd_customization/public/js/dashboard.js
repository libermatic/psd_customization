// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.provide('psd_customization');
frappe.provide('psd_customization.dashboard');

function _get_color(lifetime, to_date) {
  if (lifetime) {
    return 'green';
  }
  if (!to_date) {
    return 'darkgrey';
  }
  if (
    moment()
      .add(7, 'days')
      .isBefore(to_date)
  ) {
    return 'green';
  }
  if (moment().isSameOrBefore(to_date)) {
    return 'orange';
  }
  return 'red';
}
function _get_eta(lifetime, to_date) {
  if (lifetime) {
    return null;
  }
  return `${moment().isAfter(to_date) ? 'Expired' : 'Expires'} ${moment(
    to_date
  ).fromNow()}`;
}

psd_customization.dashboard.make_subscription_info = function(sub) {
  const { from_date, to_date, lifetime, status, subscription: link } = sub;
  return Object.assign({}, sub, {
    info: lifetime && 'Lifetime',
    warning: status !== 'Paid' && 'Unpaid',
    from_date: frappe.datetime.str_to_user(from_date),
    to_date: frappe.datetime.str_to_user(to_date),
    color: _get_color(lifetime, to_date),
    eta: _get_eta(lifetime, to_date),
    link,
  });
};

psd_customization.dashboard.make_membership_info = function(mem) {
  const { start_date, end_date, type, name: link, status: item_name } = mem;
  const lifetime = type === 'Lifetime';
  return Object.assign({}, mem, {
    item_name,
    info: lifetime && 'Lifetime',
    from_date: frappe.datetime.str_to_user(start_date),
    to_date: frappe.datetime.str_to_user(end_date),
    color: _get_color(lifetime, end_date),
    eta: _get_eta(lifetime, end_date),
    link,
  });
};
