<template>
  <div class="root psd-dashboard-section">
    <barcode-label
      v-bind="label"
      v-for="label in labels"
      :key="label.barcode"
    />
  </div>
</template>

<script>
import BarcodeLabel from './BarcodeLabel.vue';

export default {
  props: ['labels'],
  components: { BarcodeLabel },
};
</script>

<style lang="scss" scoped>
.psd-dashboard-section {
  display: flex;
  flex-flow: row nowrap;
  align-items: flex-end;
  > button {
    margin-left: 10px;
  }
}
</style>
