// Copyright (c) 2019, Libermatic and contributors
// For license information, please see license.txt

export const salary_slip = {
  set_training_data: async function(frm) {
    await frappe.call({
      method:
        'psd_customization.fitness_world.api.salary_slip.set_trainings_in_salary_slip',
      args: { doc_json: frm.doc, set_in_response: 1 },
    });
  },
  calculate_training_earnings: async function(frm) {
    const {
      salary_structure,
      total_training_months = 0,
      training_rate = 0,
    } = frm.doc;
    const {
      message: { training_salary_component } = {},
    } = await frappe.db.get_value(
      'Salary Structure',
      salary_structure,
      'training_salary_component'
    );
    const earning = frm.doc.earnings.find(
      ({ salary_component }) => salary_component === training_salary_component
    );
    if (earning) {
      earning.amount = total_training_months * training_rate;
      frm.refresh_field('earnings');
    }
  },
  toggle_training_section: function(frm) {
    frm.toggle_display(
      ['training_section', 'trainings'],
      cint(frm.doc.salary_slip_based_on_training) === 1
    );
  },
};

function calculate_training_months(frm) {
  frm.set_value(
    'actual_training_months',
    frm.doc.trainings
      .map(({ months = 0.0 }) => months)
      .reduce((a, x = 0) => a + x, 0)
  );
  frm.set_value(
    'total_training_months',
    frm.doc.trainings
      .map(
        ({ months = 0.0, cost_multiplier = 1.0 }) => months * cost_multiplier
      )
      .reduce((a, x = 0) => a + x, 0)
  );
}

export const salary_slip_training = {
  training: async function(frm, cdt, cdn) {
    const { training } = frappe.get_doc(cdt, cdn);
    if (training) {
      const no_of_occurences = frm.doc.trainings.filter(
        ({ training: t }) => t === training
      ).length;
      if (no_of_occurences > 1) {
        frm.get_field('trainings').grid.grid_rows_by_docname[cdn].remove();
      } else {
        const { start_date, end_date } = frm.doc;
        const {
          message: { months, gym_subscription, cost_multiplier } = {},
        } = await frappe.call({
          method:
            'psd_customization.fitness_world.api.salary_slip.get_training_data',
          args: { training, start_date, end_date },
        });
        frappe.model.set_value(cdt, cdn, 'months', months);
        frappe.model.set_value(cdt, cdn, 'subscription', gym_subscription);
        frappe.model.set_value(cdt, cdn, 'cost_multiplier', cost_multiplier);
      }
    } else {
      ['months', 'subscription'].forEach(field => {
        frappe.model.set_value(cdt, cdn, field, null);
      });
    }
  },
  months: function(frm, cdt, cdn) {
    calculate_training_months(frm);
  },
  trainings_remove: function(frm, cdt, cdn) {
    calculate_training_months(frm);
  },
};

export default { salary_slip, salary_slip_training };
