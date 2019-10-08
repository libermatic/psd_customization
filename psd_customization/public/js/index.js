import * as ultimate_art from './ultimate_art';
import * as utils from './utils';
import * as scripts from './scripts';
import * as custom_scripts from './custom_scripts';

frappe.ui.form.on('Sales Invoice', custom_scripts.sales_invoice);
frappe.ui.form.on('Payment Entry', custom_scripts.payment_entry);
frappe.ui.form.on('Journal Entry', custom_scripts.journal_entry);
frappe.ui.form.on('Item', custom_scripts.item);
frappe.ui.form.on('Purchase Receipt', custom_scripts.purchase_receipt);
frappe.ui.form.on(
  'Purchase Receipt Item',
  custom_scripts.purchase_receipt.purchase_receipt_item
);
frappe.ui.form.on('Purchase Invoice', custom_scripts.purchase_invoice);
frappe.ui.form.on(
  'Purchase Invoice Item',
  custom_scripts.purchase_invoice.purchase_invoice_item
);

frappe.ui.form.GymMemberQuickEntryForm = frappe.ui.form.QuickEntryForm.extend(
  scripts.gym_member.quick_entry
);

frappe.provide('psd_customization');

psd_customization = { ultimate_art, utils };
