<template>
  <div>
    <h6>Existing Subscriptions</h6>
    <div v-if="subscriptions && subscriptions.length > 0">
      <div v-for="subscription in subscriptions" :key="subscription.name">
        <current-subscription-item v-bind="subscription" />
      </div>
    </div>
    <div v-else class="psd-no-data">
      Currently none
    </div>
  </div>
</template>

<script>
import CurrentSubscriptionItem from './CurrentSubscriptionItem.vue';
export default {
  props: ['subscriptions'],
  components: { CurrentSubscriptionItem },
};
</script>

<style scoped>
.psd-no-data {
  color: #8d99a6;
}
</style>
