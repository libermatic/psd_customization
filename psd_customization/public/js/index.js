import * as ultimate_art from './ultimate_art';
import * as utils from './utils';
import * as scripts from './scripts';

frappe.ui.form.on('Sales Invoice', { company: utils.set_naming_series });
frappe.ui.form.on('Payment Entry', { company: utils.set_naming_series });
frappe.ui.form.on('Journal Entry', { company: utils.set_naming_series });

frappe.ui.form.GymMemberQuickEntryForm = frappe.ui.form.QuickEntryForm.extend(
  scripts.gym_member.quick_entry
);

frappe.provide('psd_customization');

psd_customization = { ultimate_art, utils };
