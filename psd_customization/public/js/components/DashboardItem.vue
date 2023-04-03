<template>
  <div class="col-sm-3 psd-dashboard-item">
    <span :class="indicator" />
    <dl>
      <dt>{{ label }}</dt>
      <dd>{{ content }}</dd>
    </dl>
  </div>
</template>

<script>
export default {
  props: ['label', 'content', 'color'],
  computed: {
    indicator: function () {
      return `indicator ${this.color}`;
    },
  },
};
</script>

<style scoped>
.psd-dashboard-item {
  display: flex;
  flex-flow: row nowrap;
}
.psd-dashboard-item dt {
  text-transform: uppercase;
  font-size: 0.8em;
  font-weight: normal;
}
.psd-dashboard-item dd {
  font-size: 1.2em;
  font-weight: bold;
}
</style>
