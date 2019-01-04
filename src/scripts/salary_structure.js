// Copyright (c) 2019, Libermatic and contributors
// For license information, please see license.txt

function toggle_training_fields(frm) {
  frm.toggle_display(
    ['training_salary_component', 'training_monthly_rate'],
    frm.doc.salary_slip_based_on_training
  );
}

export const salary_structure = {
  refresh: function(frm) {
    toggle_training_fields(frm);
  },
  salary_slip_based_on_training: function(frm) {
    toggle_training_fields(frm);
  },
};
