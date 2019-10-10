<template>
  <div ref="wrapper" />
</template>

<script>
import { colorHash } from '../utils/colors';
import { PercentageChart } from 'frappe-charts';

class Chart extends PercentageChart {
  renderLegend() {}
}

export default {
  props: ['schedules'],
  computed: {
    chartData: function() {
      const labels = this.schedules.map(
        ({ trainer_name }) => trainer_name || 'Unallocated'
      );
      const values = this.schedules.map(
        ({ from, to }) =>
          frappe.datetime.get_day_diff(
            frappe.datetime.user_to_str(to),
            frappe.datetime.user_to_str(from)
          ) + 1
      );
      return { labels, datasets: [{ values }] };
    },
    chartColors: function() {
      return this.schedules.map(({ trainer_name }) => colorHash(trainer_name));
    },
  },
  mounted() {
    const chart = new Chart(this.$el, {
      type: 'percentage',
      data: this.chartData,
      colors: this.chartColors,
      height: 80,
      depth: 1,
    });
    this.$watch('schedules', function() {
      chart.colors = this.chartColors;
      chart.update(this.chartData);
    });
  },
};
</script>
