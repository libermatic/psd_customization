import Vue from 'vue';

import TrainingSchedule from './TrainingSchedule.vue';
import scripts from './scripts';
import utils from './utils';

export default {
  make_training_schedule_page: node =>
    new Vue({
      el: node,
      render: h => h(TrainingSchedule),
    }),
  scripts,
  utils,
};
