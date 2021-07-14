# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

    def _prepare_payment_moves(self):
        res = super(AccountPayment, self)._prepare_payment_moves()
        _logger.debug(f'Post Payment {res}')
        _logger.debug(f'LINES {res[0]["line_ids"]}')

        for idx, line in enumerate(res[0]['line_ids']):
            _logger.debug(f'DICT {idx} {line}')
            _logger.debug(f'DICT LIne {line[0]}')

            line[2]['analytic_tag_ids'] = self.analytic_tag_ids.ids
            line[2]['analytic_account_id'] = self.analytic_account_id.id

        return res
