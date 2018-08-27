// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Subscription', {
  refresh: function(frm) {
    frm.trigger('handle_gym_member_setup');
  },
  reference_document: function(frm) {
    frm.trigger('handle_gym_member_setup');
  },
  handle_gym_member_setup: async function(frm) {
    const { reference_doctype, reference_document } = frm.doc;
    frm.toggle_display(
      'reference_gym_member',
      reference_doctype === 'Sales Invoice' && reference_document
    );
    if (reference_doctype === 'Sales Invoice' && reference_document) {
      let ref_doc = frappe.get_doc(reference_doctype, reference_document);
      let customer;
      if (ref_doc) {
        customer = ref_doc['customer'];
      } else {
        const { message = {} } = await frappe.db.get_value(
          reference_doctype,
          reference_document,
          'customer'
        );
        customer = message['customer'];
      }
      frm.set_query('reference_gym_member', () => ({
        filters: { customer },
      }));
      const { message: members = [] } = await frappe.call({
        method:
          'psd_customization.fitness_world.api.gym_member.get_members_by_customer',
        args: { customer },
      });
      if (members.length > 0) {
        frm.set_df_property('reference_gym_member', 'reqd', 1);
      }
      if (members.length === 1) {
        frm.set_value('reference_gym_member', members[0]);
      }
    } else {
      frm.set_df_property('reference_gym_member', 'reqd', 0);
    }
  },
});
