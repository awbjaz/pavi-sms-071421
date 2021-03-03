odoo.define('awb_subscriber_bill.action_button', function (require) {
  "use strict";

  var core = require('web.core');
  var ListController = require('web.ListController');
  var rpc = require('web.rpc');
  var session = require('web.session');
  var _t = core._t;

  ListController.include({
    renderButtons: function($node) {
      this._super.apply(this, arguments);
      console.log(this.$buttons);
      if (this.$buttons) {
        console.log(this.$buttons.find('.o_list_button_generate'));
        this.$buttons.find('.o_list_button_generate').click(this.proxy('generate_emp_sched'));
      }
    },

    generate_emp_sched: function () {
      var self = this;
      var user = session.uid;
      console.log('Button clicked');
      // self.do_action({
      //     name: _t('Generate Employee Schedule'),
      //     type: 'ir.actions.act_window',
      //     res_model: 'hr.employee.schedule.queue',
      //     views: [[false, 'form']],
      //     view_mode: 'form',
      //     target: 'new',
      // });
    },
  });

  console.log('registering');
  core.action_registry.add('awb_subscriber_bill.action_button', ListController);
    // return the object.

});