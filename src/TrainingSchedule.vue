<template>
  <div>
    <div class="section">
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
    </div>
    <div v-if="item_name" class="section info-section">
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
    <div class="list-section">
      <table v-if="schedules.length > 0" class="table">
        <thead>
          <tr>
            <th>From</th>
            <th>To</th>
            <th>Slot</th>
            <th>Trainer</th>
            <th />
          </tr>
        </thead>
        <tbody>
          <tr v-for="schedule in schedules">
            <td>
              {{ schedule.from }}
              <button type="button"><i class="fa fa-pencil" /></button>
            </td>
            <td>
              {{ schedule.to }}
              <button type="button"><i class="fa fa-pencil" /></button>
            </td>
            <td>
              {{ schedule.slot || '-' }}
              <button type="button"><i class="fa fa-pencil" /></button>
            </td>
            <td>
              {{ schedule.trainer || 'Unallocated' }}
              <button type="button"><i class="fa fa-plus" /></button>
              <button type="button"><i class="fa fa-remove" /></button>
            </td>
          </tr>
        </tbody>
      </table>
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
      schedules: [],
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
        const { message: trainable_items } = await frappe.call({
          method:
            'psd_customization.fitness_world.api.trainer_allocation.get_trainable_items',
          args: { subscription },
        });
        if (trainable_items) {
          this.item_name = trainable_items.items[0];
          this.start_date = frappe.datetime.str_to_user(
            trainable_items.from_date
          );
          this.end_date = frappe.datetime.str_to_user(trainable_items.to_date);
          this.get_schedules(subscription);
        }
      } else {
        this.item_name = null;
        this.start_date = null;
        this.end_date = null;
      }
    },
    get_schedules: async function(subscription) {
      const { message: schedules = [] } = await frappe.call({
        method:
          'psd_customization.fitness_world.api.trainer_allocation.get_schedule',
        args: { subscription },
      });
      this.schedules = schedules.map(
        ({ from_date, to_date, training_slot, gym_trainer }) => ({
          from: frappe.datetime.str_to_user(from_date),
          to: frappe.datetime.str_to_user(to_date),
          slot: training_slot,
          trainer: gym_trainer,
        })
      );
    },
  },
};
</script>

<style scoped>
.section {
  display: flex;
  flex-flow: row wrap;
  padding-top: 12px;
}
.section > div {
  margin: 0 8px;
  box-sizing: border-box;
  min-width: 196px;
}
.info-section > div {
  min-height: 48px;
}
.info-section > div > span {
  display: block;
  white-space: nowrap;
}
.info-section > div > span:first-of-type {
  font-size: 12px;
  color: #8d99a6;
}
.info-section > div > span:last-of-type {
  font-weight: bold;
}
.list-section button {
  border: none;
  background-color: inherit;
}
.list-section > table th {
  color: #8d99a6;
}
.list-section > table button:hover {
  color: #8d99a6;
}
</style>
