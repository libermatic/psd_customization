export class GymMemberQuickEntryForm extends frappe.ui.form.QuickEntryForm {
    render_dialog() {
      this.mandatory = this.mandatory.concat(this.get_variant_fields());
      super.render_dialog();
    }
    update_doc() {
      super.update_doc();
      this.dialog.doc.enrollment_date = frappe.datetime.get_today();
    }
    get_variant_fields() {
      return [
        {
          fieldtype: 'Section Break',
          label: __('Contact Details'),
          collapsible: 1,
        },
        {
          label: __('Email ID'),
          fieldname: 'email_id',
          fieldtype: 'Data',
        },
        {
          fieldtype: 'Column Break',
        },
        {
          label: __('Mobile Number'),
          fieldname: 'mobile_no',
          fieldtype: 'Data',
        },
        {
          fieldtype: 'Section Break',
          label: __('Address Details'),
          collapsible: 1,
        },
        {
          label: __('Address Line 1'),
          fieldname: 'address_line1',
          fieldtype: 'Data',
        },
        {
          label: __('Address Line 2'),
          fieldname: 'address_line2',
          fieldtype: 'Data',
        },
        {
          label: __('ZIP Code'),
          fieldname: 'pincode',
          fieldtype: 'Data',
        },
        {
          fieldtype: 'Column Break',
        },
        {
          label: __('City'),
          fieldname: 'city',
          fieldtype: 'Data',
        },
        {
          label: __('State'),
          fieldname: 'state',
          fieldtype: 'Data',
        },
        {
          label: __('Country'),
          fieldname: 'country',
          fieldtype: 'Link',
          options: 'Country',
          default: frappe.defaults.get_default('country'),
        },
      ];
    }
  }