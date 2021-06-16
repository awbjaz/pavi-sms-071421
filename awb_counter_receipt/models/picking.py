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


class Picking(models.Model):
    _inherit = "stock.picking"

    receipt_date_due = fields.Date(string="Receipt Date Due", compute='_compute_receipt_date_due')
    si_date = fields.Date(string="SI Date")
    si_num = fields.Char(string="SI Number")
    dr_num = fields.Char(string="DR Number")
    total_amount = fields.Float(string="Total Amount", compute='_compute_total_amount')

    @api.depends('move_ids_without_package')
    def _compute_total_amount(self):
        for rec in self:
            amount = 0
            for line in rec.move_ids_without_package:
                amount += line.quantity_done * line.purchase_line_id.price_unit
            rec.total_amount = amount


    def _get_payment_term_day(self, payment_term):
        args_term = [('payment_id', '=', payment_term),
                     ('value', '=', 'balance'),
                     ('option', '=', 'day_after_invoice_date')]
        payment_term_id = self.env['account.payment.term.line'].search(args_term)
        days = 0
        if payment_term_id:
            days = payment_term_id[0].days
        return days

    @api.depends('date_done', 'state')
    def _compute_receipt_date_due(self):
        _logger.debug(f'Process Due')
        for rec in self:
           
            due_days = self._get_payment_term_day(rec.purchase_id.payment_term_id.id)
            _logger.debug(f'Due {due_days}')
            _logger.debug(f'Date Done {rec.date_done}')
            due_date = rec.date_done
            if rec.date_done:
                due_date = rec.date_done + relativedelta(days=+due_days)
                _logger.debug(f'Due Date {due_date}')

            rec.update({
                'receipt_date_due': due_date
            })

        