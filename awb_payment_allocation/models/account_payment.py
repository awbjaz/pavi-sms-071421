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

class AccountPayment(models.Model):
    _inherit = "account.payment"

    allocation_mode = fields.Selection([('old_invoice','Oldest Invoice first'),
                                        ('high_amount','Highest Amount first'),
                                        ('low_amount','Lowest Amount first'),
                                        ('manual','Manual')], string='Allocation Mode')

    invoice_line = fields.One2many('payment.allocation.line', 'payment_id', string="Invoices")

    def action_load_invoices(self):
        _logger.debug(f'Loading Invoices')
        if not self.allocation_mode:
            raise UserError(_('Please select allocation mode first. Before loading invoices.'))
        
        order = ''
        if self.allocation_mode == 'old_invoice':
            order = 'invoice_date_due asc'
        elif self.allocation_mode == 'high_amount':
            order = 'amount_residual desc'
        elif self.allocation_mode == 'low_amount':
            order = 'amount_residual asc'

        invoices = self.env['account.move'].search([('type', '=', 'out_invoice'),('state','=','posted')], order=order)
        _logger.debug(f'Invoices {invoices}')

        invoice_line = []
        for inv in invoices:
            full_reconcile = False
            paid_amount = 0.0
            if inv.amount_residual <= self.amount:
                full_reconcile = True
                paid_amount = inv.amount_residual
            elif inv.amount_residual > self.amount:
                paid_amount = inv.amount_residual
                
            data = {
                'invoice': inv.id,
                'full_reconcile': full_reconcile,
                'paid_amount': paid_amount,
            }
            invoice_line.append((0, 0, data))
        # _logger.debug(f'Invoices {invoice_line}')
                    
        self.update({'invoice_line': None})
        self.update({'invoice_line': invoice_line})
        
        # return True


class PaymentAllocationLine(models.Model):
    _name = "payment.allocation.line"

    invoice = fields.Many2one('account.move')
    invoice_date = fields.Date(related="invoice.invoice_date", string="Invoice Date")
    due_date = fields.Date(related="invoice.invoice_date_due", string="Due Date")
    invoice_amount = fields.Monetary(related="invoice.amount_residual", string="Invoice Amount")
    currency_id = fields.Many2one(related="invoice.currency_id")
    full_reconcile = fields.Boolean(string="Full Reconcile", compute='_compute_reconcile')
    paid_amount = fields.Float(string="Paid Amount")

    payment_id = fields.Many2one('account.payment', string="Payment", ondelete="cascade", index=True, copy=False, readonly=True)

    @api.depends('invoice', 'paid_amount')
    def _compute_reconcile(self):
        full_reconcile = False
        for rec in self:
            if round(rec.invoice_amount, 2) == rec.paid_amount:
                full_reconcile = True
            rec.full_reconcile = full_reconcile
