<template>
  <div class="psd-current-sub">
    <div class="psd-current-sub-description">
      <span :class="colorClass" />
      {{ subscription.item_name }}
      <span v-if="subscription.is_lifetime" class="badge psd-badge-info">
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
  props: ['subscription'],
  methods: {
    get_color() {
      const { is_lifetime, to_date } = this.subscription;
      if (is_lifetime) {
        return 'green';
      }
      if (!to_date) {
        return 'darkgrey';
      }
      if (
        moment()
          .add(7, 'days')
          .isBefore(to_date)
      ) {
        return 'green';
      }
      if (moment().isSameOrBefore(to_date)) {
        return 'orange';
      }
      return 'red';
    },
  },
  computed: {
    colorClass: function() {
      return `indicator ${this.get_color()}`;
    },
    interval: function() {
      const { from_date, to_date } = this.subscription;
      if (to_date) {
        return `${frappe.datetime.str_to_user(
          from_date
        )} – ${frappe.datetime.str_to_user(to_date)}`;
      }
      return frappe.datetime.str_to_user(from_date);
    },
    eta: function() {
      const { from_date, to_date, is_lifetime } = this.subscription;
      if (is_lifetime && !to_date) {
        return null;
      }
      return `${moment().isAfter(to_date) ? 'Expired' : 'Expires'} ${moment(
        to_date
      ).fromNow()}`;
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
