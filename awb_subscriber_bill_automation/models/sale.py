# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

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

    def action_confirm_renewal(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'date_order': fields.Datetime.now()
        })

        for order in self:
            if any([expense_policy not in [False, 'no'] for expense_policy in order.order_line.mapped('product_id.expense_policy')]):
                if not order.analytic_account_id:
                    order._create_analytic_account()

        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        return True
