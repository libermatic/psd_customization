// Copyright (c) 2019, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Salary Slip', {
  total_training_months: async function(frm) {
    await psd.scripts.salary_slip.calculate_training_earnings(frm);
    calculate_all(frm.doc, frm.doc.doctype, frm.doc.name);
  },
  training_monthly_rate: async function(frm) {
    await psd.scripts.salary_slip.calculate_training_earnings(frm);
    calculate_all(frm.doc, frm.doc.doctype, frm.doc.name);
  },
});

frappe.ui.form.on('Salary Slip Training', psd.scripts.salary_slip_training);

get_emp_and_leave_details = async function(doc, dt, dn) {
  await frappe.call({
    method: 'get_emp_and_leave_details',
    doc: frappe.get_doc(dt, dn),
  });
  await psd.scripts.salary_slip.set_training_data({ doc });
  cur_frm.refresh();
  calculate_all(doc, dt, dn);
};
