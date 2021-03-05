# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)


class Purchase(models.Model):
    _inherit = "purchase.order"

    counter_receipt_ref = fields.Char(
        string='Counter Receipt Reference')
    counter_receipt_date = fields.Date(
        string="Counter Receipt Date")
    follow_up_to = fields.Many2one('res.partner', string="Follow Up to")

    total_amount_vendor_bills = fields.Monetary(
        string="Total Amount of Vendor Bills", compute='_compute_amount_bills')

    @api.depends('invoice_ids.amount_residual')
    def _compute_amount_bills(self):
        tot_amount = 0
        if len(self.invoice_ids) > 0:
            for line in self.invoice_ids:
                tot_amount += line.amount_residual

        self.total_amount_vendor_bills = tot_amount

    @api.model
    def create(self, vals):
        vals['counter_receipt_ref'] = self.env['ir.sequence'].next_by_code(
            'counter.receipt') or '/'

        res = super(Purchase, self).create(vals)
        _logger.debug(f'Values {vals}')
        return res
