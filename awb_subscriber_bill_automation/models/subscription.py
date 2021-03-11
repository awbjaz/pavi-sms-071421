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
        res = super(SaleSubscription, self)._prepare_invoice_line(
            line, fiscal_position, date_start, date_stop)
        if line.date_start or line.date_end:
            diff = date_stop - line.date_start
            days = diff.days
            month_factor = 31
            new_amount = 0
            if days < month_factor:
                original_amount = res['price_unit']
                rate = original_amount * 12 / 365
                new_amount = rate * days
                res['price_unit'] = new_amount
                res['name'] += f' ({days} days)'
            _logger.debug(
                f'Prorate: {diff} = {new_amount} {line} {fiscal_position} {date_start} {date_stop}')
        # if self.subscription_status == 'new' and diff.days < 31:
        return res

    def _prepare_invoice_lines(self, fiscal_position):
        self.ensure_one()
        if not self.subscriber_location_id.cutoff_day:
            raise UserError('No Zone is assigned to subscriber location. Please assign a zone on subscriber record.')
        cutoff_day = self.subscriber_location_id.cutoff_day
        next_date = self.recurring_next_date

        if not next_date:
            raise UserError(_('Please define Date of Next Invoice of "%s".') % (self.display_name,))

        periods = {'daily': 'days', 'weekly': 'weeks',
                   'monthly': 'months', 'yearly': 'years'}
        interval_type = periods[self.recurring_rule_type]
        interval = self.recurring_interval

        next_date = next_date - relativedelta(**{interval_type: interval*2})
        _logger.debug(f'Compute next date: Next {next_date}, due_day: {cutoff_day}')
        recurring_start_date = self._get_recurring_next_date(self.recurring_rule_type, interval, next_date, cutoff_day)
        revenue_date_start = fields.Date.from_string(recurring_start_date+relativedelta(days=1))
        _logger.debug('Dates: Next Date: {next_date} Start Day: {revenue_date_start}')
        recurring_next_date = self._get_recurring_next_date(self.recurring_rule_type, interval, revenue_date_start, cutoff_day)
        revenue_date_stop = fields.Date.from_string(recurring_next_date)
        invoice_lines = []
        for line in self.recurring_invoice_line_ids:
            starts_within = not line.date_start or (line.date_start and line.date_start < revenue_date_stop)
            ends_within = not line.date_end or (line.date_end and line.date_end > revenue_date_start)
            _logger.debug(f'Check Invoice line dates: {starts_within} {line.date_start} {revenue_date_stop}')
            _logger.debug(f'Check Invoice line dates: {ends_within} {line.date_end} {revenue_date_start}')
            if starts_within and ends_within:
                val = self._prepare_invoice_line(
                    line, fiscal_position, revenue_date_start, revenue_date_stop)
                invoice_lines.append((0, 0, val))
        return invoice_lines

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

            total_vat = 0.0
            for taxes in line['tax_ids']:
                vat = taxes[2]
                args = [('id', 'in', vat)]
                tax = self.env['account.tax'].search(args)
                total_price_unit = line['price_unit'] * \
                    line['quantity']  # 1999
                tot_vat = 0.0
                for t in tax:
                    total_price_unit = total_price_unit - tot_vat
                    # tax exclusive
                    # total_vat += total_price_unit * tax.amount / 100
                    # tax inclusive
                    tot_vat += (total_price_unit /
                                ((100 + t.amount) / 100)) * (t.amount/100)
                total_vat += tot_vat

            if product.product_tmpl_id.id == device_id:
                data = {
                    'name': line['name'],
                    'statement_type': 'device_fee',
                    'amount': line['price_unit'] - total_vat,
                }
                lines.append((0, 0, data))
            else:

                data = {
                    'name': line['name'],
                    'statement_type': 'subs_fee',
                    'amount': line['price_unit'] - total_vat,
                }
                lines.append((0, 0, data))

            data = {'name': "Value Added Tax", 'statement_type': 'vat'}
            data['amount'] = total_vat
            lines.append((0, 0, data))

        # invoice previous bill
        args = [('partner_id', '=', invoice['partner_id']),
                ('type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_line_ids.subscription_id', '=', self.id)]

        invoice_id = self.env['account.move'].search(args, limit=1, order="date desc")

        if invoice_id:
            prev_bill = invoice_id.amount_total + invoice_id.total_prev_charges
            prev_bill = {
                'name': 'Previous Bill balance',
                'statement_type': 'prev_bill',
                'amount': prev_bill,
            }
            lines.append((0, 0, prev_bill))

        #Previous Payment
        args_pay = [('partner_id', '=', invoice['partner_id']),
                    ('partner_type', '=', 'customer'),
                    ('state', '=', 'posted')]
        payment_id = self.env['account.payment'].search(args_pay, limit=1, order="payment_date desc")


        if payment_id:
            prev_payment = payment_id.amount
            prev_payment = {
                'name': 'Previous Received Payment',
                'statement_type': 'payment',
                'amount': prev_payment * -1,
            }
            lines.append((0, 0, prev_payment))

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


class SaleSubscriptionLine(models.Model):
    _inherit = "sale.subscription.line"

    date_start = fields.Date(string='Start Date', default=fields.Date.today)
    date_end = fields.Date(string='End Date')
