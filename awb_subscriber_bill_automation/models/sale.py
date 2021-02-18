# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_subscription_data(self, template):
        res = super(SaleOrder,
                    self)._prepare_subscription_data(template)
        if self.opportunity_id:
            res['opportunity_id'] = self.opportunity_id.id
            res['subscriber_location_id'] = self.opportunity_id.zone
            res['account_identification'] = self.account_identification
            res['date_start'] = self.opportunity_id.contract_start_date
            if self.opportunity_id.zone.billing_day:
                recurring_invoice_day = self.opportunity_id.zone.billing_day

                date_today = res['date_start']
                recurring_next_date = self.env['sale.subscription']._get_recurring_next_date(
                    template.recurring_rule_type, template.recurring_interval,
                    date_today, recurring_invoice_day
                )

                res['recurring_next_date'] = recurring_next_date
                res['recurring_invoice_day'] = recurring_invoice_day

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
