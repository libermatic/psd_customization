frappe.pages['training-schedule'].on_page_load = function(wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'Training Schedule',
    single_column: true,
  });
  psd.make_training_schedule_page(page.body[0]);
};
