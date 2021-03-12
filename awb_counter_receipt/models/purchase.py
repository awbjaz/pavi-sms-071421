# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class Purchase(models.Model):
    _inherit = "purchase.order"

    counter_receipt_ref = fields.Char(string='Counter Receipt Reference')
    counter_receipt_date = fields.Date(string="Counter Receipt Date")
    follow_up_to = fields.Many2one('res.partner', string="Follow Up to")
    total_amount_vendor_bills = fields.Monetary(string="Total Amount of Vendor Bills",
                                                compute='_compute_amount_bills')
    receipt_date_due = fields.Date(string="Receipt Date Due")
    si_num  = fields.Char(string="SI No.")
    dr_num = fields.Char(string="DR No.")
    mrr_num = fields.Char(string="MRR No.")

    def _get_date_receipt(self, po_id, partner):
        args_pick = [('purchase_id', '=', po_id),
                     ('partner_id', '=', partner),
                     ('state', '=', 'done')]
        pick_id = self.env['stock.picking'].search(args_pick, limit=1, order="date_done desc")

        effective_date = False
        if pick_id:
            effective_date = pick_id.date_done

        return effective_date

    def _get_payment_term_day(self, payment_term):
        args_term = [('payment_id', '=', payment_term),
                     ('value', '=', 'balance'),
                     ('option', '=', 'day_after_invoice_date')]
        payment_term_id = self.env['account.payment.term.line'].search(args_term)
        days = 0
        if payment_term_id:
            days = payment_term_id[0].days
        return days

    @api.onchange('payment_term_id')
    def _onchange_receipt_date_due(self):
        due_date = None
        date = self._get_date_receipt(self._origin.id, self.partner_id.id)
        due_days = self._get_payment_term_day(self.payment_term_id.id)
        if date:
            due_date = date + relativedelta(days=+due_days)

        self.update({
            'receipt_date_due': due_date
        })

        _logger.debug(f'pickings {due_date}')

    @api.depends('invoice_ids.amount_residual')
    def _compute_amount_bills(self):
        tot_amount = 0
        if len(self.invoice_ids) > 0:
            for line in self.invoice_ids:
                tot_amount += line.amount_residual

        self.total_amount_vendor_bills = tot_amount

    @ api.model
    def create(self, vals):
        vals['counter_receipt_ref'] = self.env['ir.sequence'].next_by_code(
            'counter.receipt') or '/'

        res = super(Purchase, self).create(vals)
        _logger.debug(f'Values {vals}')
        return res
