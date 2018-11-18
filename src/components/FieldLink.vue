<template>
  <field
    v-bind="{ fieldname, label, options, get_query }"
    :onblur="onchange"
    :fieldtype="'Link'"
  />
</template>

<script>
import Field from './Field.vue';
export default {
  components: { Field },
  props: ['fieldname', 'label', 'options', 'get_query', 'onchange'],
};
</script>
