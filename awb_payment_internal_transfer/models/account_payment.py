# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
   _inherit = "account.payment"

   source_payment_id = fields.Many2one('account.payment', string="Source Payment", readonly=True)
   date_transfer = fields.Date(string="Transfer Date")
   transfer_details = fields.One2many('account.payment.transfer', 'payment_id', string="Transfer Details", readonly=True)
   is_deposited = fields.Boolean(string="Deposited")

   def post(self):
      res = super(AccountPayment, self).post()
      self.is_deposited = True

      for rec in self.transfer_details:
         item.is_deposited = True

   def verify_payment(self, payment_ids):
      _logger.debug(f'Payments Record {payment_ids}')
      payments = self.env['account.payment'].browse(payment_ids)
      total_amount = sum([pay.amount for pay in payments])

      journals = []
      for pay in payments:
         if pay.payment_type == 'transfer':
            journals.append(pay.destination_journal_id.id)
         else:
            journals.append(pay.journal_id.id)

      _logger.debug(f'Journal {journals}')

      has_internal_transfer = []
      for line in payments:
         if line.source_payment_id.state == 'posted':
            has_internal_transfer.append(line.name)

      if(len(set(journals))!=1):
            raise UserError(_('Please select Payment Record with a same "Journal" to create payment internal transfer.'))

      elif any(line.state != 'posted' for line in payments):
            raise UserError(_('Please select Payment which are in "Validated" state to create payment internal transfer.'))

      elif any(line.source_payment_id.state == 'posted' for line in payments):
            raise UserError(_('%s has already payment internal transfer. Please select Payment that does not have payment internal transfer.')% ','.join(
               map(str, has_internal_transfer)))

      else:
         return {
            'type': 'ir.actions.act_window',
            'res_model': 'payment.internal.transfer',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {
               'default_source_journal_id': journals[0] or False,
               'default_total_amount': total_amount,
               'payment_obj': payment_ids, 
            },
         }


class AccountPaymentTransfer(models.Model):
   _name = "account.payment.transfer"
   _description = "Account Payment Transfer"

   payment_id = fields.Many2one('account.payment', string="Payment")
   payment_ref = fields.Many2one('account.payment', string="Payment Reference")
   partner_id = fields.Many2one('res.partner', string="Partner")
   amount = fields.Float(string="Amount")
   memo = fields.Char(string="Memo")
   payment_date = fields.Date(string="Payment Date")
    
