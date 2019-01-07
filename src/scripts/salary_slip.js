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
};

export default { salary_slip };
