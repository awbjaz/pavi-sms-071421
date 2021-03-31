import calendar
import datetime
import pprint

from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class AccountAsset(models.Model):
    _inherit = 'account.asset'

    first_depreciation_date  = fields.Date(string="First Depreciation Date", readonly=True, required=True, store=True, compute='_default_first_depreciation_date')

    # trigger_first_depreciation_date  = fields.Date(string="First Depreciation Date", readonly=True, store=False, compute='_default_trigger_first_depreciation_date', default=datetime.datetime.now())

    # @api.depends("trigger_first_depreciation_date", "acquisition_date")
    # @api.depends("acquisition_date")
    def _default_first_depreciation_date(self):
        _logger.error('_default_first_depreciation_date')
        return self._compute_depreciation_date(self.acquisition_date) 

    def _default_trigger_first_depreciation_date(self):
        _logger.error('_default_trigger_first_depreciation_date')
        return self._compute_depreciation_date(self.acquisition_date) 

    def _get_first_depreciation_date_str(self, vals={}):
        _logger.error('_get_first_depreciation_date')
        first_depreciation_date = self._compute_depreciation_date(vals.get('acquisition_date', datetime.datetime.now()))
        return str(first_depreciation_date)

    def _compute_depreciation_date(self, acquisition_date):
        _logger.error('_compute_depreciation_date')
        base_date = acquisition_date
        _logger.error('_compute_depreciation_date: ' + str(base_date))

        # if no base date 
        if base_date is None or base_date is False:
            base_date = datetime.datetime.now()

        # if base date is in string format
        if isinstance(base_date, str):
            base_date = datetime.datetime.strptime(base_date, '%Y-%m-%d').date()
        _logger.error('_compute_depreciation_date: ' + str(base_date))

        try:
            day = base_date.day
        except:
            _logger.error('_compute_depreciation_date: exception caught')
            base_date = datetime.datetime.now()
            day = base_date.day

        month = base_date.month
        year = base_date.year

        if day > 15:
            month = month + 1

        if month > 12:
            month = 1
            year = year + 1

        day = calendar.monthrange(year, month)[1]

        _logger.error('_compute_depreciation_date: ' + str(year) + ' ' + str(month) + ' ' + str(day))
        return datetime.date(year, month, day)

    def write(self, vals):
        _logger.error('write')
        _logger.error(pprint.pformat(vals, indent=4))
        if vals.get('acquisition_date'):
            vals['first_depreciation_date'] = self._get_first_depreciation_date_str(vals)
        _logger.error(pprint.pformat(vals, indent=4))
        result = super(AccountAsset, self).write(vals)
        return result

    @api.onchange('acquisition_date')
    def onchange_acquisition_date(self):
        _logger.error('onchange_acquisition_date')
        self.first_depreciation_date = self._compute_depreciation_date(self.acquisition_date)

    @api.onchange('first_depreciation_date')
    def onchange_first_depreciation_date(self):
        _logger.error('onchange_first_depreciation_date')
        expected = self._compute_depreciation_date(self.acquisition_date)
        if self.first_depreciation_date != expected:
            self.first_depreciation_date = expected 
