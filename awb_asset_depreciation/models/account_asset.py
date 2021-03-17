import calendar
import datetime

from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class AccountAsset(models.Model):
    _inherit = 'account.asset'
    
    first_depreciation_date  = fields.Date(string="First Depreciation Date", readonly=True, required=True, stored=True, default=datetime.datetime.today())

    def compute_depreciation_date(self, acquisition_date):
        if acquisition_date:
            day = acquisition_date.day
            month = acquisition_date.month
            year = acquisition_date.year

            if day > 15:
                month = month + 1

            day = calendar.monthrange(year, month)[1]

            return datetime.date(year, month, day)

    @api.model   
    def create(self, vals):
        _logger.error('create')
        try:
            if vals.has_key('acquisition_date'):
                vals['first_depreciation_date'] = self.compute_depreciation_date(vals['acquisition_date'])
        except:
            pass #evil

        result = super(AccountAsset, self).create(vals)
        return result 

    @api.onchange('acquisition_date')
    def onchange_acquisition_date(self):
        _logger.error('onchange_acquisition_date')
        if self.acquisition_date:
            self.first_depreciation_date = self.compute_depreciation_date(self.acquisition_date)

    @api.onchange('first_depreciation_date')
    def onchange_first_depreciation_date(self):
        _logger.error('onchange_first_depreciation_date')
        if self.acquisition_date:
            expected = self.compute_depreciation_date(self.acquisition_date)
            if self.first_depreciation_date != expected:
                self.first_depreciation_date = expected 
                           
