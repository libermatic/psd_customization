import Vue from 'vue';

import TrainingSchedule from './TrainingSchedule.vue';
import MemberDashboard from './MemberDashboard.vue';
import SubscriptionDashboard from './SubscriptionDashboard.vue';
import CurrentSubscriptions from './components/CurrentSubscriptions.vue';
import docscripts from './docscripts';
import components from './frappe-components';
import utils from './utils';
import transform from './transform';

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
  make_subscription_details: (node, props) =>
    new Vue({
      el: node,
      render: h => h(CurrentSubscriptions, { props }),
    }),
  make_training_schedule_page: node =>
    new Vue({
      el: node,
      render: h => h(TrainingSchedule),
    }),
  docscripts,
  components,
  utils,
  transform,
};
