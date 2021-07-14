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


class AccountMove(models.Model):
    _inherit = "account.move"

    posting_date = fields.Date(string="Posting Date")

    def action_cron_posting_invoice(self):
        today = fields.Date.today()
        account_moves = self.env['account.move']
        moves = account_moves.search(
            [('state', '=', 'draft'), ('posting_date', '<=', today)], limit=200)
        _logger.debug(f'Record {moves}')

        for rec in moves:
            try:
                rec.action_approve()
                rec.action_post()
                self.env.cr.commit()
            except Exception as e:
                _logger.info(f'Error {e}')
