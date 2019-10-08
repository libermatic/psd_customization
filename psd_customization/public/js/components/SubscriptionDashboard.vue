<template>
  <div class="row">
    <dashboard-item v-bind="invoice_cpt" />
  </div>
</template>

<script>
import DashboardItem from './DashboardItem.vue';

function get_color(status) {
  if (status === 'Paid') {
    return 'green';
  }
  if (status === 'Unpaid') {
    return 'orange';
  }
  if (status === 'Overdue') {
    return 'red';
  }
  return 'blue';
}

export default {
  props: ['invoice'],
  components: { DashboardItem },
  computed: {
    invoice_cpt: function() {
      const { amount, status } = this.invoice || {};
      return {
        label: 'Invoice Amount',
        content: amount
          ? format_currency(amount, frappe.defaults.get_default('currency'))
          : '-',
        color: get_color(status),
      };
    },
  },
};
</script>
