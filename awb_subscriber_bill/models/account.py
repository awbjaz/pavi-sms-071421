# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models, _
from datetime import datetime, date

import logging

from ..helpers.printer_data_util import PrinterDataUtil

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    statement_line_ids = fields.One2many('account.statement.line', 'move_id', string="Statement Line")
    atm_ref = fields.Char(string="ATM Reference", compute="_compute_atm_reference_number", stored=True)
    atm_ref_sequence = fields.Char(string="ATM Reference Sequence", stored=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    period_covered = fields.Date(string="Period Covered")
    total_statement_balance = fields.Monetary(string="Total Statement Balance", compute='_compute_statement_balance')
    total_prev_charges = fields.Monetary(string="Total Previous Charges", compute='_compute_statement_balance')
    is_subscription = fields.Boolean(string="Is Subscribtion", compute="_compute_is_subscription")
    total_vat = fields.Float(string="Total Vat", compute='_compute_statement_balance')

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
            rec.total_vat = sum(
                rec.statement_line_ids.filtered(lambda r: r.statement_type == 'vat').mapped('amount'))
            prev_balance = sum(rec.statement_line_ids.filtered(lambda r: r.statement_type == 'prev_bill').mapped('amount'))
            prev_received = sum(rec.statement_line_ids.filtered(lambda r: r.statement_type == 'payment').mapped('amount'))
            rec.total_prev_charges = prev_balance + prev_received

    @api.model
    def create(self, vals):
        vals['atm_ref_sequence'] = self.env['ir.sequence'].next_by_code('account_move.atm.reference.seq.code')
        res = super(AccountMove, self).create(vals)
        return res

    @api.depends("atm_ref_sequence")
    def _compute_atm_reference_number(self):
        for rec in self:
            rec.atm_ref = ''
            if rec.atm_ref_sequence:
                today = date.today()
                year = str(today.year)[2:4]
                sequence = rec.atm_ref_sequence
                company_code = rec.company_id.zone_code
                value = f'{year}-{company_code}-{sequence}-1231'
                rec.atm_ref = value

    def action_cron_generate(self):
        records = self.env['account.move'].search(
            [('type', 'in', ['out_invoice', 'in_invoice'])])
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

            lines = []
            # invoice Lines
            for line in rec.invoice_line_ids:
                if line.product_id.product_tmpl_id.id == self.env.ref('awb_subscriber_product_information.product_device_fee').id:
                    data = {
                        'name': line.name,
                        'statement_type': 'device_fee',
                        'amount': line.credit,
                    }
                    _logger.debug(
                        f'Prod ID temp {line.product_id.product_tmpl_id.id}')
                    lines.append((0, 0, data))
                else:
                    data = {
                        'name': line.name,
                        'statement_type': 'subs_fee',
                        'amount': line.credit,
                    }
                    lines.append((0, 0, data))

            # taxes
            for line in rec.line_ids:
                if line.tax_line_id:
                    data = {'name': "Value Added Tax",
                            'statement_type': 'vat'}
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
                    'name': 'Payment',
                    'statement_type': 'payment',
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
                    'statement_type': 'credit',
                    'amount': total_amount * -1,
                }

                lines.append((0, 0, data))
            prod_id = self.env.ref(
                'awb_subscriber_product_information.product_device_fee').id
            _logger.debug(f'Prod ID {prod_id}')
            _logger.debug(f'Inv Lines {rec.name}{lines}')
            rec.update({'statement_line_ids': None})
            rec.update({'statement_line_ids': lines})

    def export_printer_data_file(self):
        url = "/print/custom/sales_invoice/%s" % self.id
        return {
            "url": url,
            "type": "ir.actions.act_url"
        }

    def export_printer_data_file_from_many(self, account_ids):
        _logger.error(f'export_printer_data_file_from_many {account_ids}')

        # records = self.env['account.move'].search([('id', 'in', account_ids)])
        # return PrinterDataUtil.generate_data_file(records)
        
        string_ids = [str(int) for int in account_ids]
        url = "/print/custom/sales_invoice/%s" % '-'.join(string_ids)
        return {
            "url": url,
            "type": "ir.actions.act_url"
        }

class AccountStatementLine(models.Model):
    _name = "account.statement.line"

    name = fields.Char(string="Description")
    amount = fields.Float(string="Amount")
    statement_type = fields.Selection([('subs_fee', 'Subscription Fee'),
                                       ('device_fee', 'Device Fee'),
                                       ('vat', 'VAT'),
                                       ('prev_bill', 'Previous Bill'),
                                       ('payment', 'Previous Received Payment'),
                                       ('adjust', 'Adjustment'),
                                       ('other', 'Other')], string="Statement Type")

    move_id = fields.Many2one('account.move', string="Invoice")
