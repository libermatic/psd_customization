// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

export function get_gym_item_description({
  item_name,
  gym_is_lifetime,
  gym_from_date,
  gym_to_date,
}) {
  if (gym_is_lifetime) {
    return `${item_name}: Lifetime validity, starting ${frappe.datetime.str_to_user(
      gym_from_date
    )}`;
  }
  return `${item_name}: Valid from ${frappe.datetime.str_to_user(
    gym_from_date
  )} to ${frappe.datetime.str_to_user(gym_to_date)}`;
}

export function set_si_item_qty(frm, cdt, cdn) {}

export default { get_gym_item_description };
