frappe.pages['training-schedule'].on_page_load = function(wrapper) {
  wrapper.page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'Training Schedule',
    single_column: true,
  });
  frappe.breadcrumbs.add('Fitness World');
};

frappe.pages['training-schedule'].refresh = function({ page }) {
  psd.make_training_schedule_page(page.body[0], {
    defaults: frappe.route_options || {},
  });
};
