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
              <button
                v-if="schedule.name"
                type="button"
                name="update_from_date"
                @click="update(schedule.name, 'from_date')"
              >
                <i class="fa fa-pencil" />
              </button>
            </td>
            <td>
              {{ schedule.to }}
              <button
                v-if="schedule.name"
                type="button"
                name="update_to_date"
                @click="update(schedule.name, 'to_date')"
              >
                <i class="fa fa-pencil" />
              </button>
            </td>
            <td>
              {{ schedule.slot || '-' }}
              <button
                v-if="schedule.name"
                type="button"
                name="update_slot"
                @click="update(schedule.name, 'slot')"
              >
                <i class="fa fa-pencil" />
              </button>
            </td>
            <td>
              {{ schedule.trainer_name || 'Unallocated' }}
              <button
                v-if="!schedule.name"
                type="button"
                name="create"
                @click="create(schedule.from, schedule.to)"
              >
                <i class="fa fa-plus" />
              </button>
              <button
                v-else
                type="button"
                name="remove"
                @click="remove(schedule.name)"
              >
                <i class="fa fa-remove" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import FieldLink from './components/FieldLink.vue';
import frappeAsync from './utils/frappe-async';

const default_subscription_filter = { docstatus: 1 };

function make_dialog_field(what) {
  const field = { fieldname: 'value', reqd: 1 };
  if (['from_date', 'to_date'].includes(what)) {
    return [Object.assign(field, { fieldtype: 'Date', label: 'Date' })];
  }
  if (what === 'slot') {
    return [
      Object.assign(field, {
        fieldtype: 'Link',
        label: 'Slot',
        options: 'Training Slot',
      }),
    ];
  }
  if (what === 'trainer') {
    return [
      Object.assign(field, {
        fieldtype: 'Link',
        label: 'Trainer',
        options: 'Gym Trainer',
      }),
    ];
  }
  return null;
}

export default {
  data() {
    return {
      subscription_query: { filters: default_subscription_filter },
      subscription: null,
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
        this.subscription = subscription;
        this.get_schedules();
        const {
          message: { subscription_name, from_date, to_date } = {},
        } = await frappe.db.get_value('Gym Subscription', subscription, [
          'subscription_name',
          'from_date',
          'to_date',
        ]);
        this.item_name = subscription_name;
        this.start_date = frappe.datetime.str_to_user(from_date);
        this.end_date = frappe.datetime.str_to_user(to_date);
      } else {
        this.subscription = null;
        this.item_name = null;
        this.start_date = null;
        this.end_date = null;
      }
    },
    get_schedules: async function() {
      const { message: schedules = [] } = await frappe.call({
        method:
          'psd_customization.fitness_world.api.trainer_allocation.get_schedule',
        args: { subscription: this.subscription },
      });
      this.schedules = schedules.map(
        ({
          name,
          from_date,
          to_date,
          training_slot,
          gym_trainer,
          gym_trainer_name,
        }) => ({
          name,
          from: frappe.datetime.str_to_user(from_date),
          to: frappe.datetime.str_to_user(to_date),
          slot: training_slot,
          trainer: gym_trainer,
          trainer_name: gym_trainer_name,
        })
      );
    },
    create: async function(from_date, to_date) {
      const { value: trainer } = await frappeAsync.prompt(
        make_dialog_field('trainer'),
        'Select Trainer'
      );
      await frappe.call({
        method: 'psd_customization.fitness_world.api.trainer_allocation.create',
        args: {
          subscription: this.subscription,
          trainer,
          from_date: frappe.datetime.user_to_str(from_date),
          to_date: frappe.datetime.user_to_str(to_date),
        },
        freeze: true,
      });
      this.get_schedules();
    },
    update: async function(name, key) {
      const field = make_dialog_field(key);
      const { value } = await frappeAsync.prompt(
        field,
        field && field.fieldtype === 'Date' ? 'Enter Date' : 'Select Slot'
      );
      await frappe.call({
        method: 'psd_customization.fitness_world.api.trainer_allocation.update',
        args: { name, key, value },
        freeze: true,
      });
      this.get_schedules();
    },
    remove: async function(name) {
      const will_remove = await frappeAsync.confirm(
        'Trainer for this period will be unassigned'
      );
      if (will_remove) {
        await frappe.call({
          method:
            'psd_customization.fitness_world.api.trainer_allocation.remove',
          args: { name },
          freeze: true,
        });
      }
      this.get_schedules();
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
  opacity: 0;
}
.list-section tr:hover button {
  opacity: 1;
}
.list-section > table th {
  color: #8d99a6;
}
.list-section > table button:hover {
  color: #8d99a6;
}
</style>
