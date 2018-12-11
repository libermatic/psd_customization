<template>
  <field :df="df" :events="events" />
</template>

<script>
import Field from './Field.vue';
export default {
  components: { Field },
  props: ['fieldname', 'label', 'options', 'get_query', 'onchange'],
  computed: {
    df: function() {
      const { fieldname, label, options, get_query } = this;
      const fieldtype = 'Link';
      return {
        fieldname,
        fieldtype,
        label,
        options,
        get_query,
      };
    },
    events: function() {
      return {
        'awesomplete-selectcomplete': e => {
          this.onchange({ fieldname: this.fieldname, value: e.target.value });
        },
      };
    },
  },
};
</script>
