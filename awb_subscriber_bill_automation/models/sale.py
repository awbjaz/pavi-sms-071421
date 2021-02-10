# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_subscription_data(self, template):
        res = super(SaleOrder,
                    self)._prepare_subscription_data(template)
        if self.opportunity_id:
            res['account_identification'] = self.account_identification

        _logger.debug(f'Result {res}')
        return res
