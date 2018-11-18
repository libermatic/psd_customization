<template>
  <div>
    <div class="row">
      <dashboard-item v-bind="outstanding_cpt" />
      <dashboard-item v-bind="invoices" />
    </div>
    <current-subscriptions :subscriptions="subscriptions"/>
  </div>
</template>

<script>
import DashboardItem from './components/DashboardItem.vue';
import CurrentSubscriptions from './components/CurrentSubscriptions.vue';

export default {
  props: ['outstanding', 'total_invoices', 'unpaid_invoices', 'subscriptions'],
  components: { DashboardItem, CurrentSubscriptions },
  computed: {
    outstanding_cpt: function() {
      return {
        label: 'Current Outstanding',
        content: this.outstanding
          ? format_currency(
              this.outstanding,
              frappe.defaults.get_default('currency')
            )
          : '-',
        color: this.outstanding ? 'orange' : 'lightblue',
      };
    },
    invoices: function() {
      return {
        label: 'Invoices: All / Unpaid',
        content: `${this.unpaid_invoices || '-'} / ${this.total_invoices ||
          '-'}`,
        color: this.unpaid_invoices ? 'orange' : 'green',
      };
    },
  },
};
</script>
