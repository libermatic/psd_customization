<template>
  <field v-bind="{ df, events, value }" />
</template>

<script>
import Field from './Field.vue';
export default {
  components: { Field },
  props: [
    'fieldname',
    'value',
    'label',
    'options',
    'read_only',
    'get_query',
    'onchange',
  ],
  computed: {
    df: function () {
      const { fieldname, label, options, read_only, get_query } = this;
      const fieldtype = 'Link';
      return {
        fieldname,
        fieldtype,
        label,
        options,
        read_only,
        get_query,
      };
    },
    events: function () {
      return {
        'awesomplete-selectcomplete': (e) => {
          this.onchange({ fieldname: this.fieldname, value: e.target.value });
        },
      };
    },
  },
};
</script>
