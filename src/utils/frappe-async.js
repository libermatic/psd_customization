// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

export const prompt = function(fields, title, primary_label) {
  return new Promise(function(resolve, reject) {
    try {
      return frappe.prompt(
        fields,
        values => (values ? resolve(values) : reject()),
        title,
        primary_label
      );
    } catch (e) {
      reject(e);
    }
  });
};

export const confirm = function(message) {
  return new Promise(function(resolve, reject) {
    try {
      return frappe.confirm(message, () => resolve(true), () => resolve(false));
    } catch (e) {
      reject(e);
    }
  });
};

export default {
  prompt,
  confirm,
};
