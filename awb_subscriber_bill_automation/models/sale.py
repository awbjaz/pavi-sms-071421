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

    outside_source = fields.Boolean(string="Outside Source")

    def _prepare_subscription_data(self, template):
        res = super(SaleOrder,
                    self)._prepare_subscription_data(template)
        if self.opportunity_id:
            res['opportunity_id'] = self.opportunity_id.id
        _logger.debug(f'Result {res}')
        return res
