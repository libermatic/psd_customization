// Copyright (c) 2019, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Salary Slip', {
  setup: function(frm) {
    frm.fields_dict['trainings'].grid.get_field(
      'training'
    ).get_query = function() {
      return {
        query: 'psd_customization.fitness_world.api.salary_slip.training_query',
        filters: { employee: frm.doc.employee },
      };
    };
  },
  refresh: function(frm) {
    psd.scripts.salary_slip.toggle_training_section(frm);
  },
  salary_slip_based_on_training: function(frm) {
    psd.scripts.salary_slip.toggle_training_section(frm);
  },
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
