# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class PaymentInternalTransfer(models.TransientModel):
    _name = 'payment.internal.transfer'

    source_journal_id = fields.Many2one('account.journal', string="Source Journal", readonly=True)
    dest_journal_id = fields.Many2one('account.journal', string="Destination Journal", required=True, domain=[('type', 'in', ('bank','cash'))])
    total_amount = fields.Float(string="Total Amount", readonly=True)


    def create_transfer_payment(self):
        payments = self.env['account.payment'].browse(self._context['payment_obj'])
        _logger.debug(f'Payments {payments}')

        paymethod_obj = self.env['account.payment.method']
        payment_method = paymethod_obj.search([('payment_type', '=', 'inbound')])
        if payment_method:
            payment_method_id = payment_method[0]
        else:
            raise UserError("No payment method defined.")

        transfer_details = []
        for payment in payments:
            transfer_details.append((0, 0, {
                'payment_ref': payment.id,
                'partner_id': payment.partner_id.id,
                'amount': payment.amount,
                'memo': payment.communication,
                'payment_date': payment.payment_date,
            }))

        data = {
            'journal_id': self.source_journal_id.id,
            'destination_journal_id': self.dest_journal_id.id,
            'payment_date': fields.Date.today(),
            'amount': self.total_amount,
            'payment_method_id': payment_method_id.id,
            'payment_type': 'transfer',
            'transfer_details': transfer_details,
            }

        payment_id = self.env['account.payment'].create(data)

        _logger.debug(f'Payment {payment_id}')
        _logger.debug(f'Payment data {data}')

        for rec in payments:
            rec.source_payment_id = payment_id.id

        return payment_id


    def open_create_internal_payment(self):
        internal_payment_id = self.create_transfer_payment()
        _logger.debug(f'internal_payment_id {internal_payment_id.id}')

        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('account.action_account_payments')
        form_view_id = imd.xmlid_to_res_id('account.view_account_payment_form')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[form_view_id, 'form']],
            'target': action.target,
            'res_model': action.res_model,
            'res_id': internal_payment_id.id,
        }
        result['domain'] = "[('id','=',%s)]" % internal_payment_id.id
        return result
