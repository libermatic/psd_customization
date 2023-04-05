import * as utils from './utils';
import * as scripts from './scripts';
import * as quick_entry from './quick_entry';
import * as cscripts from './custom_scripts';
import TrainingSchedule from './components/TrainingSchedule.vue';
import { __version__ } from './version';

frappe.ui.form.GymMemberQuickEntryForm =
  scripts.gym_member.GymMemberQuickEntryForm;

frappe.provide('psd_customization');

frappe.provide('psd');
psd = {
  make_training_schedule_page: (node, props) =>
    new Vue({
      el: node,
      render: (h) => h(TrainingSchedule, { props }),
    }),
  scripts,
  utils,
  __version__,
};

Object.keys(quick_entry).forEach((import_name) => {
  const handler = quick_entry[import_name];
  frappe.ui.form[import_name] = handler;
});

function get_doctype(import_name) {
  return import_name
    .split('_')
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(' ');
}

Object.keys(cscripts).forEach((import_name) => {
  const handler = cscripts[import_name];
  frappe.ui.form.on(get_doctype(import_name), handler);
});
