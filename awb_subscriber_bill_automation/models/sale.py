# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models, _
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

        self.update_existing_subscriptions()
        self.create_subscriptions()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        return True


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    date_start = fields.Date(string='Start Date', default=fields.Date.today)
    date_end = fields.Date(string='End Date')

    def _prepare_subscription_line_data(self):
        """Prepare a dictionnary of values to add lines to a subscription."""
        values = list()
        for line in self:
            values.append((0, False, {
                'product_id': line.product_id.id,
                'name': line.name,
                'quantity': line.product_uom_qty,
                'uom_id': line.product_uom.id,
                'price_unit': line.price_unit,
                'discount': line.discount if line.order_id.subscription_management != 'upsell' else False,
                'date_start': line.date_start,
                'date_end': line.date_end
            }))
        return values
