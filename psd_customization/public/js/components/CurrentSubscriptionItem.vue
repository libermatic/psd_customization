<template>
  <div class="psd-current-sub">
    <div class="psd-current-sub-description">
      <span :class="colorClass" />
      <a :href="docUrl">{{ item_name }}</a>
      <span
        v-if="is_lifetime && status === 'Active'"
        class="badge psd-badge-info"
      >
        Lifetime
      </span>
    </div>
    <div class="psd-current-sub-interval">
      {{ interval }}
    </div>
    <div class="psd-current-sub-remarks">
      {{ eta }}
    </div>
  </div>
</template>

<script>
export default {
  props: ['name', 'item_name', 'is_lifetime', 'from_date', 'to_date', 'status'],
  methods: {
    get_color() {
      const { is_lifetime, to_date, status } = this;
      if (status !== 'Active') {
        return 'red';
      }
      if (is_lifetime) {
        return 'green';
      }
      if (!to_date) {
        return 'darkgrey';
      }
      const day_after = moment(to_date).add(1, 'd');
      if (moment().add(7, 'days').isBefore(day_after)) {
        return 'green';
      }
      if (moment().isSameOrBefore(day_after)) {
        return 'orange';
      }
      return 'red';
    },
  },
  computed: {
    docUrl: function () {
      return `/app/gym-subscription/${encodeURIComponent(this.name)}`;
    },
    colorClass: function () {
      return `indicator ${this.get_color()}`;
    },
    interval: function () {
      const { from_date, to_date } = this;
      if (to_date) {
        return `${frappe.datetime.str_to_user(
          from_date
        )} – ${frappe.datetime.str_to_user(to_date)}`;
      }
      return frappe.datetime.str_to_user(from_date);
    },
    eta: function () {
      const { from_date, to_date, is_lifetime } = this;
      if (is_lifetime && !to_date) {
        return null;
      }
      const day_after = moment(to_date).add(1, 'd');
      return `${
        moment().isAfter(day_after) ? 'Expired' : 'Expires'
      } ${day_after.fromNow()}`;
    },
  },
};
</script>

<style scoped>
.psd-current-sub {
  display: flex;
  flex-flow: row wrap;
  font-size: 0.94em;
}
.psd-current-sub > div {
  flex: 0 0 30%;
}
.psd-current-sub > div:first-of-type {
  flex: auto;
}
.badge {
  font-variant: all-small-caps;
}
.psd-badge-info {
  background-color: #935eff;
  color: #ffffff;
}
.psd-info_item-badge-warning {
  background-color: #ffa00a;
}
</style>
