// Copyright (c) 2019, Libermatic and contributors
// For license information, please see license.txt

get_emp_and_leave_details = async function(doc, dt, dn) {
  await frappe.call({
    method: 'get_emp_and_leave_details',
    doc: frappe.get_doc(dt, dn),
  });
  await psd.scripts.salary_slip.set_training_data({ doc });
  cur_frm.refresh();
  calculate_all(doc, dt, dn);
};
