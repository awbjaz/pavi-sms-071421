# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models


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
            'default_outside_source': self.outside_source,
        })
        _logger.debug(f'Result {result}')
        return result

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if self.stage_id.is_auto_quotation:
            if self.subscription_status == 'new':
                plan = []
                for line in self.plan.sale_order_template_line_ids:
                    data = {
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'product_uom_qty': line.product_uom_qty,
                        'price_unit': line.price_unit,
                    }
                    plan.append((0, 0, data))

                lines = []
                data = {
                    'account_identification': self.account_identification,
                    'sale_order_template_id': self.plan.id,
                    'date_order': self.contract_start_date,
                    'outside_source': self.outside_source,
                    'opportunity_id': self._origin.id,
                    'partner_id': self.partner_id.id,
                    'team_id': self.team_id.id,
                    'campaign_id': self.campaign_id.id,
                    'medium_id': self.medium_id.id,
                    'origin': self.name,
                    'source_id': self.source_id.id,
                    'company_id': self.company_id.id or self.env.company.id,
                    'tag_ids': [(6, 0, self.tag_ids.ids)],
                    'order_line': plan
                }

                lines.append((0, 0, data))
                _logger.debug(f'Get Lines {lines}')

                sale_order_id = self.env['sale.order'].create(data)
                sale_order_id.action_confirm()
                _logger.debug(f'Sale Order {sale_order_id}')

    def write(self, values):
        # Change Subscription Status
        if values.get('subscription_status'):
            for order in self.order_ids:
                if order.order_line:
                    for line in order.order_line:
                        if line.subscription_id:
                            line.subscription_id.update(
                                {'subscription_status': values.get('subscription_status')})
        _logger.debug(f"Change Status {values.get('subscription_status')}")

        if values.get('subscription_status') == 'disconnection':
            if self.stage_id.is_auto_quotation:
                for order in self.order_ids:
                    if order.order_line:
                        for line in order.order_line:
                            if line.subscription_id:
                                line.subscription_id.update({'stage_id': self.env.ref(
                                    'sale_subscription.sale_subscription_stage_closed').id})
                                _logger.debug(f'Order Name {line.name}')
                                _logger.debug(
                                    f'Order Name {line.subscription_id.stage_id}')
        _logger.debug(f'Values {values}')

        if values.get('subscription_status') == 'pre-termination':
            if self.stage_id.is_auto_quotation:
                for order in self.order_ids:
                    if order.order_line:
                        for line in order.order_line:
                            if line.subscription_id:
                                line.subscription_id.update({'stage_id': self.env.ref(
                                    'sale_subscription.sale_subscription_stage_closed').id})
        # renewal
        if values.get('subscription_status') == 'upgrade' or values.get('subscription_status') == 'convert':
            if self.stage_id.is_auto_quotation:
                subscription = []
                for order in self.order_ids:
                    if order.subscription_management == 'create':
                        if order.order_line:
                            for line in order.order_line:
                                if line.subscription_id:
                                    if line.subscription_id.id not in subscription:
                                        subscription.append(line.subscription_id.id)

                subscription_id = self.env['sale.subscription'].search([('id', 'in', subscription)])
                for subs_id in subscription_id:
                    subs_id.update({'to_renew': True})
                    subs_id.prepare_renewal_order()
                    _logger.debug(f'Subs ID {subs_id}')

        _logger.debug(f'Values {values}')
        return super(CRMLead, self).write(values)
