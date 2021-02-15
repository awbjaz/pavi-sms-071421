# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    account_identification = fields.Char(string="Account ID")
    subscription_status = fields.Selection([('new', 'New'),
                                            ('upgrade', 'Upgrade'),
                                            ('convert', 'Convert'),
                                            ('downgrade', 'Downgrade'),
                                            ('re-contract', 'Re-contract'),
                                            ('pre-termination', 'Pre-Termination'),
                                            ('disconnection', 'Disconnection'),
                                            ('reconnection', 'Reconnection')], default='new', string="Subscription Status")

    def _prepare_renewal_values(self, product_lines, opportunity_id):
        res = dict()
        for subscription in self:
            fpos_id = self.env['account.fiscal.position'].with_context(
                force_company=subscription.company_id.id).get_fiscal_position(subscription.partner_id.id)
            addr = subscription.partner_id.address_get(['delivery', 'invoice'])
            sale_order = subscription.env['sale.order'].search(
                [('order_line.subscription_id', '=', subscription.id)],
                order="id desc", limit=1)
            res[subscription.id] = {
                'pricelist_id': subscription.pricelist_id.id,
                'partner_id': subscription.partner_id.id,
                'partner_invoice_id': addr['invoice'],
                'partner_shipping_id': addr['delivery'],
                'currency_id': subscription.pricelist_id.currency_id.id,
                'order_line': product_lines,
                'analytic_account_id': subscription.analytic_account_id.id,
                'subscription_management': 'renew',
                'origin': subscription.code,
                'note': subscription.description,
                'fiscal_position_id': fpos_id,
                'user_id': subscription.user_id.id,
                'payment_term_id': sale_order.payment_term_id.id if sale_order else subscription.partner_id.property_payment_term_id.id,
                'company_id': subscription.company_id.id,
                'opportunity_id': opportunity_id,
            }
        return res

    def prepare_renewal(self, product_lines, opportunity_id):
        self.ensure_one()
        values = self._prepare_renewal_values(product_lines, opportunity_id)
        order = self.env['sale.order'].create(values[self.id])
        order.message_post(body=(_("This renewal order has been created from the subscription ") +
                                 " <a href=# data-oe-model=sale.subscription data-oe-id=%d>%s</a>" % (self.id, self.display_name)))
        order.order_line._compute_tax_id()
        _logger.debug(f'Order pro {order}')
        _logger.debug(f'Order product_lines {product_lines}')
        order.action_confirm_renewal()
