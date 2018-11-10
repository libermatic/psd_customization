<template>
  <div class="container">
    <FieldLink
      fieldname="member"
      label="Member"
      options="Gym Member"
      :onchange="set_subscription_query"
    />
    <FieldLink
      fieldname="subscription"
      label="Subscription"
      options="Gym Subscription"
      :get_query="subscription_query"
      :onchange="get_subscription"
    />
    <div>
      <div>
        <span>Item</span>
        <span>{{ item_name }}</span>
      </div>
      <div>
        <span>Start Date</span>
        <span>{{ start_date }}</span>
      </div>
      <div>
        <span>End Date</span>
        <span>{{ end_date }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import FieldLink from './components/FieldLink.vue';

const default_subscription_filter = { docstatus: 1 };

export default {
  data() {
    return {
      subscription_query: { filters: default_subscription_filter },
      item_name: null,
      start_date: null,
      end_date: null,
    };
  },
  components: { FieldLink },
  methods: {
    set_subscription_query: function(member) {
      this.subscription_query = {
        filters: member
          ? Object.assign({}, default_subscription_filter, { member })
          : default_subscription_filter,
      };
    },
    get_subscription: async function(subscription) {
      if (subscription) {
        const { message } = await frappe.call({
          method:
            'psd_customization.fitness_world.api.trainer_allocation.get_trainable_items',
          args: { subscription },
        });
        if (message) {
          this.item_name = message.items[0];
          this.start_date = frappe.datetime.str_to_user(message.from_date);
          this.end_date = frappe.datetime.str_to_user(message.end_date);
        }
      } else {
        this.item_name = null;
        this.start_date = null;
        this.end_date = null;
      }
    },
  },
};
</script>

<style scoped>
.container {
  display: flex;
  padding-top: 12px;
}
.container > div {
  margin: 0 8px;
}
</style>
