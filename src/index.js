import Vue from 'vue';

import TrainingSchedule from './TrainingSchedule.vue';
import components from './frappe-components';

export default {
  make_training_schedule_page: node =>
    new Vue({
      el: node,
      render: h => h(TrainingSchedule),
    }),
  components,
};
