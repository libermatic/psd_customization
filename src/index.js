import Vue from 'vue';

import TrainingSchedule from './TrainingSchedule.vue';

export default {
  make_training_schedule_page: node =>
    new Vue({
      el: node,
      render: h => h(TrainingSchedule),
    }),
};
