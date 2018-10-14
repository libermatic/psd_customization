// Copyright (c) 2018, Libermatic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gym Membership', {
  refresh: function(frm) {
    if (!frm.doc.__islocal) {
      frm.trigger('add_actions');
    }
  },
  add_actions: function(frm) {
    const { status } = frm.doc;
    const status_props = {
      Active: { label: 'Stop', status_to_change: 'Stopped' },
      Stopped: { label: 'Resume', status_to_change: 'Active' },
    };
    if (status_props[status]) {
      const { label, status_to_change } = status_props[status];
      frm
        .add_custom_button(label, async function() {
          await frappe.call({
            method:
              'psd_customization.fitness_world.api.gym_membership.set_status',
            args: { name: frm.doc['name'], status: status_to_change },
          });
          frm.reload_doc();
        })
        .toggleClass('btn-primary', status === 'Active');
    }
  },
});
