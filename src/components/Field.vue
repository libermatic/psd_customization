<template>
  <div ref="wrapper" />
</template>

<script>
export default {
  props: {
    df: Object,
    events: Object,
    value: String,
  },
  mounted() {
    const { read_only, ...df } = this.df;
    const field = frappe.ui.form.make_control({ parent: this.$el, df });
    field.refresh();
    Object.keys(this.events).forEach(evt => {
      field.$input.on(evt, this.events[evt]);
    });
    this.$once('hook:beforeDestroy', function() {
      Object.keys(this.events).forEach(evt => {
        field.$input.off(evt, this.events[evt]);
      });
      field.$wrapper.remove();
    });
    this.$watch('df.get_query', function(query) {
      field.get_query = query;
      field.set_custom_query({});
    });
    this.$watch('df.read_only', function(read_only) {
      this.set_attrib(field, 'read_only', read_only);
    });
    this.$watch('value', function(value) {
      field.set_value(value);
    });
    if (this.value) {
      field.set_value(this.value);
    }
    if (read_only) {
      this.set_attrib(field, 'read_only', read_only);
    }
  },
  methods: {
    set_attrib: function(field, attrib, value) {
      field.df[attrib] = value ? 1 : 0;
      field.refresh();
    },
  },
};
</script>
