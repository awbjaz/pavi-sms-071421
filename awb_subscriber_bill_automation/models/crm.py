# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class CRMLead(models.Model):
    _inherit = "crm.lead"

    def action_new_quotation(self):
        result = super(CRMLead, self).action_new_quotation()
        result['context'].update({
            'default_account_identification': self.account_identification,
            'default_sale_order_template_id': self.plan.id,
            'default_date_order': self.contract_start_date,
            'default_outside_sourced': self.outside_source,
        })
        _logger.debug(f'Result {result}')
        return result

    @api.onchange('stage_id')
    def _onchange_bill_stage_id(self):
        if self.stage_id.is_auto_quotation:
            if self.subscription_status == 'new':
                product_lines = []
                for line in self.product_lines:
                    data = {
                        'product_id': line.product_id.id,
                        'name': line.product_id.name,
                        'product_uom_qty': line.quantity,
                        'price_unit': line.unit_price,
                    }
                    product_lines.append((0, 0, data))

                lines = []
                data = {
                    'account_identification': self.account_identification,
                    'sale_order_template_id': self.plan.id,
                    'date_order': self.contract_start_date,
                    'outside_sourced': self.outside_source,
                    'opportunity_id': self._origin.id,
                    'partner_id': self.partner_id.id,
                    'team_id': self.team_id.id,
                    'campaign_id': self.campaign_id.id,
                    'medium_id': self.medium_id.id,
                    'origin': self.name,
                    'source_id': self.source_id.id,
                    'company_id': self.company_id.id or self.env.company.id,
                    'tag_ids': [(6, 0, self.tag_ids.ids)],
                    'order_line': product_lines
                }

                lines.append((0, 0, data))
                _logger.debug(f'Get Lines {lines}')

                sale_order_id = self.env['sale.order'].create(data)
                sale_order_id.action_confirm()
                _logger.debug(f'Sale Order {sale_order_id}')

            elif self.subscription_status == 'disconnection' or self.subscription_status == 'pre-termination':
                subscriber_id = self.env['sale.subscription'].search([('partner_id', '=', self.partner_id.id), (
                    'account_identification', '=', self.account_identification), ('stage_id', '!=', self.env.ref(
                        'sale_subscription.sale_subscription_stage_closed').id)])

                for subs in subscriber_id:
                    subs.update({'stage_id': self.env.ref('sale_subscription.sale_subscription_stage_closed').id,
                                 'subscription_status': self.subscription_status,
                                 })

                _logger.debug(f'Disconnect {subscriber_id}')

            elif self.subscription_status == 'reconnection':
                subscriber_id = self.env['sale.subscription'].search([('partner_id', '=', self.partner_id.id), (
                    'account_identification', '=', self.account_identification), ('stage_id', '=', self.env.ref(
                        'sale_subscription.sale_subscription_stage_closed').id)], order='date_start desc', limit=1)

                subscriber_id.update({'stage_id': self.env.ref('sale_subscription.sale_subscription_stage_in_progress').id,
                                      'subscription_status': self.subscription_status,
                                      })
                _logger.debug(f'Reconnect {subscriber_id}')

            elif self.subscription_status == 'upgrade' or self.subscription_status == 'convert' or self.subscription_status == 'downgrade':
                subscriber_id = self.env['sale.subscription'].search([('partner_id', '=', self.partner_id.id), (
                    'account_identification', '=', self.account_identification), ('stage_id', '!=', self.env.ref(
                        'sale_subscription.sale_subscription_stage_closed').id)])

                product_lines = []
                for line in self.product_lines:
                    data = {
                        'product_id': line.product_id.id,
                        'name': line.product_id.name,
                        'product_uom_qty': line.quantity,
                        'price_unit': line.unit_price,
                    }
                    product_lines.append((0, 0, data))

                for subs in subscriber_id:
                    subs.subscription_status = self.subscription_status
                    subs.prepare_renewal(
                        product_lines,  opportunity_id=self._origin.id)

                    _logger.debug(f'Pro {self._origin.id}')
                _logger.debug(f'Upgrade {subscriber_id}')
