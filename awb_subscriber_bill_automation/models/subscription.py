# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    account_identification = fields.Char(string="Account ID")
    opportunity_id = fields.Many2one('crm.lead', string='Opportunity')
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

    def _prepare_invoice_line(self, line, fiscal_position, date_start=False, date_stop=False):
        res = super(SaleSubscription, self)._prepare_invoice_line(line, fiscal_position, date_start, date_stop)
        diff = date_stop - self.date_start
        days = diff.days
        month_factor = 31
        new_amount = 0
        if days < month_factor:
            original_amount = res['price_unit']
            rate = original_amount * 12 / 365
            new_amount = rate * days
            res['price_unit'] = new_amount
            res['name'] += f' ({days} days)'
        _logger.debug(f'Prorate: {diff} = {new_amount} {line} {fiscal_position} {date_start} {date_stop}')
        # if self.subscription_status == 'new' and diff.days < 31:
        return res

    def _prepare_invoice_lines(self, fiscal_position):
        self.ensure_one()
        due_day = self.subscriber_location_id.billing_due_day
        next_date = self.recurring_next_date

        if not next_date:
            raise UserError(_('Please define Date of Next Invoice of "%s".') % (self.display_name,))

        periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
        interval_type = periods[self.recurring_rule_type]
        interval = self.recurring_interval

        next_date = next_date - relativedelta(**{interval_type: interval*2})
        _logger.debug(f'Compute next date: Next {next_date}, due_day: {due_day}')
        recurring_start_date = self._get_recurring_next_date(self.recurring_rule_type, interval, next_date, due_day)
        revenue_date_start = fields.Date.from_string(recurring_start_date+relativedelta(days=1))
        recurring_next_date = self._get_recurring_next_date(self.recurring_rule_type, interval, revenue_date_start, due_day)
        revenue_date_stop = fields.Date.from_string(recurring_next_date)
        return [(0, 0, self._prepare_invoice_line(line, fiscal_position, revenue_date_start, revenue_date_stop)) for line in self.recurring_invoice_line_ids]

    def _prepare_invoice_statement(self, invoice):
        self.ensure_one()
        device_id = self.env.ref('awb_subscriber_product_information.product_device_fee').id
        lines = []
        # invoice Lines
        for invoice_line in invoice['invoice_line_ids']:
            line = invoice_line[2]
            _logger.debug(f'Line: {line}')
            product = self.env['product.product'].browse(line['product_id'])
            _logger.debug(f'Prod ID temp {product.product_tmpl_id.id}')
            if product.product_tmpl_id.id == device_id:
                data = {
                    'name': line['name'],
                    'statement_type': 'device_fee',
                    'amount': line['price_unit'],
                }
                lines.append((0, 0, data))
            else:
                data = {
                    'name': line['name'],
                    'statement_type': 'subs_fee',
                    'amount': line['price_unit'],
                }
                lines.append((0, 0, data))
        return lines

    def _prepare_invoice(self):
        invoice = super(SaleSubscription, self)._prepare_invoice()
        invoice['statement_line_ids'] = self._prepare_invoice_statement(invoice)
        return invoice

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

    def wipe(self):
        self.write({"recurring_invoice_line_ids": [(6, 0, [])]})

    @api.onchange('date_start', 'template_id')
    def onchange_date_start(self):
        if self.date_start and self.recurring_rule_boundary == 'limited' and self.opportunity_id:
            periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
            contract_term = self.opportunity_id.contract_term
            self.date = fields.Date.from_string(self.date_start) + relativedelta(**{
                periods[self.recurring_rule_type]: contract_term * self.template_id.recurring_interval})
        else:
            self.date = False
