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
