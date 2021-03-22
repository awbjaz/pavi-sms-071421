import calendar
import datetime

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
        return self.compute_depreciation_date(self.acquisition_date) 

    def _default_trigger_first_depreciation_date(self):
        _logger.error('_default_trigger_first_depreciation_date')
        return self.compute_depreciation_date(self.acquisition_date) 

    def _get_first_depreciation_date(self, vals={}):
        _logger.error('_get_first_depreciation_date')
        first_depreciation_date = self.compute_depreciation_date(vals.get('acquisition_date', datetime.datetime.now()))
        return first_depreciation_date

    def compute_depreciation_date(self, acquisition_date):
        _logger.error('compute_depreciation_date')
        base_date = acquisition_date
        if base_date is None or base_date is False or base_date is True:
            base_date = datetime.datetime.now()

        try:
            day = base_date.day
        except:
            base_date = datetime.datetime.now()
            day = base_date.day

        month = base_date.month
        year = base_date.year

        if day > 15:
            month = month + 1

        day = calendar.monthrange(year, month)[1]

        return datetime.date(year, month, day)

    @api.model
    def create(self, vals):
        _logger.error('create')
        vals['first_depreciation_date'] = self.compute_depreciation_date(vals.get('acquisition_date', datetime.datetime.now()))

        result = super(AccountAsset, self).create(vals)
        return result 

    @api.onchange('acquisition_date')
    def onchange_acquisition_date(self):
        _logger.error('onchange_acquisition_date')
        self.first_depreciation_date = self.compute_depreciation_date(self.acquisition_date)

    @api.onchange('first_depreciation_date')
    def onchange_first_depreciation_date(self):
        _logger.error('onchange_first_depreciation_date')
        expected = self.compute_depreciation_date(self.acquisition_date)
        if self.first_depreciation_date != expected:
            self.first_depreciation_date = expected 
                           

    