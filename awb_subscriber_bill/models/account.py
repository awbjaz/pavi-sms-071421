
# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from barcode import Code39
from barcode.writer import ImageWriter
import io
import base64

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
        invoice_type = vals.get('type', self._context.get('default_type', 'entry'))
        if invoice_type == 'out_invoice':
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
                value = f'{year}{company_code}{sequence}1231'
                rec.atm_ref = value

    def print_atm_ref(self, atm_ref):
        return atm_ref[2:]

    def action_generate_barcode(self, number):
        number = self.print_atm_ref(number)
        _logger.debug(f'Generating Barcode: {number}')
        img_writer = ImageWriter()
        img_writer.text_distance = 0.1
        img = Code39(number, add_checksum=False, writer=img_writer)
        f = io.BytesIO()
        img.write(f)
        img_data = base64.b64encode(f.getvalue()).decode()
        return img_data

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

    def recompute_statement(self):
        self.ensure_one()
        device_id = self.env.ref('awb_subscriber_product_information.product_device_fee').id
        lines = []
        # invoice Lines
        for invoice in self.invoice_line_ids:
            if invoice.product_id.product_tmpl_id.id == device_id:
                data = {
                    'name': invoice.name,
                    'statement_type': 'device_fee',
                    'amount': invoice.price_subtotal,
                }
                lines.append((0, 0, data))

            elif invoice.subscription_id:
                data = {
                    'name': invoice.name,
                    'statement_type': 'subs_fee',
                    'amount': invoice.price_subtotal,
                }
                lines.append((0, 0, data))

            else:
                data = {
                    'name': invoice.name,
                    'statement_type': 'other',
                    'amount': invoice.price_subtotal,
                }
                lines.append((0, 0, data))

        data = {'name': "Value Added Tax", 'statement_type': 'vat'}
        data['amount'] = self.amount_tax
        lines.append((0, 0, data))

        # invoice previous bill
        args = [('partner_id', '=', self.partner_id.id),
                ('type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('is_subscription', '=', True),
                ('id', '!=', self.id)]

        invoice_id = self.env['account.move'].search(args, limit=1, order="end_date desc")
        _logger.debug(f' prev_ball {invoice_id}')
        if invoice_id:
            prev_bill = invoice_id.amount_total + invoice_id.total_prev_charges
            prev_bill = {
                'name': 'Previous Bill balance',
                'statement_type': 'prev_bill',
                'amount': prev_bill,
            }
            lines.append((0, 0, prev_bill))

        #Previous Payment
        args_pay = [('partner_id', '=', self.partner_id.id),
                    ('partner_type', '=', 'customer'),
                    ('invoice_ids', 'in', invoice_id.id),
                    ('state', '=', 'posted')]
        payment_id = self.env['account.payment'].search(args_pay, limit=1, order="payment_date desc")
        _logger.debug(f' prev_pay {payment_id}')

        if payment_id:
            prev_payment = payment_id.amount
            prev_payment = {
                'name': 'Previous Received Payment',
                'statement_type': 'payment',
                'amount': prev_payment * -1,
            }
            lines.append((0, 0, prev_payment))


        self.update({'statement_line_ids': None})
        self.update({'statement_line_ids': lines})


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
