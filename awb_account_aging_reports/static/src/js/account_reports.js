odoo.define('awb_account_aging_reports.account_report', function (require) {
'use strict';

var core = require('web.core');
var accountReportsWidget = require('account_reports.account_report');
var RelationalFields = require('web.relational_fields');
var StandaloneFieldManagerMixin = require('web.StandaloneFieldManagerMixin');
var Widget = require('web.Widget');

var QWeb = core.qweb;
var _t = core._t;

// INHERITED FROM account_reports.account_report
var M2MFilters = Widget.extend(StandaloneFieldManagerMixin, {
    /**
     * @constructor
     * @param {Object} fields
     */
    init: function (parent, fields) {
        this._super.apply(this, arguments);
        StandaloneFieldManagerMixin.init.call(this);
        this.fields = fields;
        this.widgets = {};
    },
    /**
     * @override
     */
    willStart: function () {
        var self = this;
        var defs = [this._super.apply(this, arguments)];
        _.each(this.fields, function (field, fieldName) {
            defs.push(self._makeM2MWidget(field, fieldName));
        });
        return Promise.all(defs);
    },
    /**
     * @override
     */
    start: function () {
        var self = this;
        var $content = $(QWeb.render("m2mWidgetTable", {fields: this.fields}));
        self.$el.append($content);
        _.each(this.fields, function (field, fieldName) {
            self.widgets[fieldName].appendTo($content.find('#'+fieldName+'_field'));
        });
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * This method will be called whenever a field value has changed and has
     * been confirmed by the model.
     *
     * @private
     * @override
     * @returns {Promise}
     */
    _confirmChange: function () {
        var self = this;
        var result = StandaloneFieldManagerMixin._confirmChange.apply(this, arguments);
        var data = {};
        _.each(this.fields, function (filter, fieldName) {
            data[fieldName] = self.widgets[fieldName].value.res_ids;
        });
        this.trigger_up('value_changed', data);
        return result;
    },
    /**
     * This method will create a record and initialize M2M widget.
     *
     * @private
     * @param {Object} fieldInfo
     * @param {string} fieldName
     * @returns {Promise}
     */
    _makeM2MWidget: function (fieldInfo, fieldName) {
        var self = this;
        var options = {};
        options[fieldName] = {
            options: {
                no_create_edit: true,
                no_create: true,
            }
        };
        return this.model.makeRecord(fieldInfo.modelName, [{
            fields: [{
                name: 'id',
                type: 'integer',
            }, {
                name: 'display_name',
                type: 'char',
            }],
            name: fieldName,
            relation: fieldInfo.modelName,
            type: 'many2many',
            value: fieldInfo.value,
        }], options).then(function (recordID) {
            self.widgets[fieldName] = new RelationalFields.FieldMany2ManyTags(self,
                fieldName,
                self.model.get(recordID),
                {mode: 'edit',}
            );
            self._registerWidget(recordID, fieldName, self.widgets[fieldName]);
        });
    },
});

var accountReportsWidgetFilter = accountReportsWidget.include({
  custom_events: {
      'value_changed': function(ev) {
          var self = this;
          self.report_options.partner_ids = ev.data.partner_ids;
          self.report_options.partner_categories = ev.data.partner_categories;
          self.report_options.analytic_accounts = ev.data.analytic_accounts;
          self.report_options.analytic_tags = ev.data.analytic_tags;
          self.report_options.account_accounts = ev.data.account_accounts;
          return self.reload().then(function () {
              if (ev.data.partner_categories || ev.data.partner_ids){
                self.$searchview_buttons.find('.account_partner_filter').click();
              } else if (ev.data.analytic_accounts || ev.data.analytic_tags || ev.data.account_accounts) {
                self.$searchview_buttons.find('.account_analytic_filter').click();
              }
          });
       },
  },
  render_searchview_buttons: function (){
    this._super.apply(this, arguments);
    if (this.report_options.partner) {
        if (!this.M2MFilters) {
            var fields = {};
            if ('partner_ids' in this.report_options) {
                fields['partner_ids'] = {
                    label: _t('Partners'),
                    modelName: 'res.partner',
                    value: this.report_options.partner_ids.map(Number),
                };
            }
            if ('partner_categories' in this.report_options) {
                fields['partner_categories'] = {
                    label: _t('Tags'),
                    modelName: 'res.partner.category',
                    value: this.report_options.partner_categories.map(Number),
                };
            }
            if (!_.isEmpty(fields)) {
                this.M2MFilters = new M2MFilters(this, fields);
                this.M2MFilters.appendTo(this.$searchview_buttons.find('.js_account_partner_m2m'));
            }
        } else {
            this.$searchview_buttons.find('.js_account_partner_m2m').append(this.M2MFilters.$el);
        }
    }

    if (this.report_options.analytic) {
      if (!this.AnalyticFilters) {
        var fields = {};
        if (this.report_options.analytic_accounts) {
            fields['analytic_accounts'] = {
                label: _t('Analytic Accounts'),
                modelName: 'account.analytic.account',
                value: this.report_options.analytic_accounts.map(Number),
            };
        }
        if (this.report_options.analytic_tags) {
            fields['analytic_tags'] = {
                label: _t('Tags'),
                modelName: 'account.analytic.tag',
                value: this.report_options.analytic_tags.map(Number),
            };
        }
        if (this.report_options.account_accounts){
            fields['account_accounts'] = {
                label: _t('Accounts'),
                modelName: 'account.account',
                value: this.report_options.account_accounts.map(Number),
            };
        }
        if (!_.isEmpty(fields)) {
            this.AnalyticFilters = new M2MFilters(this, fields);
            this.AnalyticFilters.appendTo(this.$searchview_buttons.find('.js_account_analytic_m2m'));
        }
      } else {
        this.$searchview_buttons.find('.js_account_analytic_m2m').html(this.AnalyticFilters.$el);
      }
    }
  }
})

});