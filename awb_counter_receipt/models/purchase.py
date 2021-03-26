# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class Purchase(models.Model):
    _inherit = "purchase.order"

    counter_receipt_ref = fields.Char(string='Counter Receipt Reference')
    counter_receipt_date = fields.Date(string="Counter Receipt Date")
    follow_up_to = fields.Many2one('res.partner', string="Follow Up to")

    @ api.model
    def create(self, vals):
        vals['counter_receipt_ref'] = self.env['ir.sequence'].next_by_code(
            'counter.receipt') or '/'

        res = super(Purchase, self).create(vals)
        _logger.debug(f'Values {vals}')
        return res
