<template>
  <div ref="wrapper" />
</template>

<script>
export default {
  props: {
    fieldtype: String,
    fieldname: String,
    label: String,
    options: String,
    get_query: Object,
    onblur: Function,
  },
  mounted() {
    const {
      fieldtype,
      fieldname,
      label,
      get_query,
      options,
      onblur = () => {},
    } = this;
    const field = frappe.ui.form.make_control({
      parent: this.$el,
      df: { fieldtype, fieldname, label, get_query, options },
    });
    field.refresh();
    field.$input.on('blur', () => {
      onblur(field.get_value());
    });
    this.$once('hook:beforeDestroy', function() {
      field.$input.off('blur');
      field.$wrapper.remove();
    });
    this.$watch('get_query', function(query) {
      field.get_query = query;
      field.set_custom_query({});
    });
  },
};
</script>
