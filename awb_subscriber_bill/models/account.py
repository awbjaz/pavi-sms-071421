# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    statement_line_ids = fields.One2many('account.statement.line', 'move_id', string="Statement Line")
    atm_ref = fields.Char(string="ATM Reference")
    period_covered = fields.Datetime(string="Period Covered")
    total_statement_balance = fields.Float(string="Total Statement Balance", compute='_compute_statement_balance')
    is_subscription = fields.Boolean(string="Is Subscribtion", compute="_compute_is_subscription")

    @api.depends('invoice_line_ids')
    def _compute_is_subscription(self):
        for rec in self:
            rec.is_subscription = False
            if rec.invoice_line_ids:
                for line in rec.invoice_line_ids:
                    if line.subscription_id:
                        rec.is_subscription = True
                    
    @api.depends('statement_line_ids')
    def _compute_statement_balance(self):
        for rec in self:
            rec.total_statement_balance = sum(
                rec.statement_line_ids.mapped('amount'))

    def action_cron_generate(self):
        records = self.env['account.move'].search([('type', 'in', ['out_invoice', 'in_invoice'])])
        _logger.debug(f'Record Invoice and Bill {records}')

        for rec in records:
            args = [('partner_id', '=', rec.partner_id.id),
                    ('company_id', '=', rec.company_id.id),
                    ('state', '=', 'posted'),
                    ('invoice_ids', 'in', rec.id)]
            payments = rec.env['account.payment'].search(args)

            args_refund = [('partner_id', '=', rec.partner_id.id),
                           ('company_id', '=', rec.company_id.id),
                           ('state', '=', 'posted'),
                           ('reversed_entry_id', '=', rec.id)]

            refunds = rec.env['account.move'].search(args_refund)

            _logger.debug(f'Refunds {refunds}')

            code = ''
            if rec.partner_id.subscriber_location_id.code:
                code = rec.partner_id.subscriber_location_id.code + '-'
            
            if rec.invoice_date_due:
                ref_date = '-' + rec.invoice_date_due.strftime('%m%y')
            else:
                ref_date = ''

            rec.atm_ref = f'{code}{rec.id:06}{ref_date}'

            lines = []
            # invoice Lines
            for line in rec.invoice_line_ids:
                data = {
                    'name': line.name,
                    'amount': line.credit,
                }
                lines.append((0, 0, data))
            # taxes
            for line in rec.line_ids:
                if line.tax_line_id:
                    data = {'name': line.name}
                    if line.tax_line_id.type_tax_use == 'sale':
                        data['amount'] = line.credit
                    elif line.tax_line_id.type_tax_use == 'purchase':
                        data['amount'] = line.debit
                    else:
                        data['amount'] = 0.0
                    lines.append((0, 0, data))

            # payments
            if payments:
                total_amount = 0
                for line in payments:
                    total_amount += line.amount

                data = {
                    'name': 'Payments',
                    'amount': total_amount * -1,
                }

                lines.append((0, 0, data))

            # refunds
            if refunds:
                total_amount = 0
                for line in refunds:
                    total_amount += (line.amount_total - line.amount_residual)
                data = {
                    'name': 'Credits/Rebates',
                    'amount': total_amount * -1,
                }

                lines.append((0, 0, data))

            _logger.debug(f'Inv Lines {rec.name}{lines}')
            rec.update({'statement_line_ids': None})
            rec.update({'statement_line_ids': lines})


class AccountStatementLine(models.Model):
    _name = "account.statement.line"

    name = fields.Char(string="Description")
    amount = fields.Float(string="Amount")

    move_id = fields.Many2one('account.move', string="Invoice")
