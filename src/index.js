import Vue from 'vue';

import TrainingSchedule from './TrainingSchedule.vue';
import MemberDashboard from './MemberDashboard.vue';
import SubscriptionDashboard from './SubscriptionDashboard.vue';
import scripts from './scripts';
import utils from './utils';

export default {
  make_member_dashboard: (node, props) =>
    new Vue({
      el: node,
      render: h => h(MemberDashboard, { props }),
    }),
  make_subscription_dashboard: (node, props) =>
    new Vue({
      el: node,
      render: h => h(SubscriptionDashboard, { props }),
    }),
  make_training_schedule_page: node =>
    new Vue({
      el: node,
      render: h => h(TrainingSchedule),
    }),
  scripts,
  utils,
};
