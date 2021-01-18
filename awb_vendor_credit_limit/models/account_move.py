from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"
    _description = "Journal Entries"

    def vendor_check_limit(self):
        partner = self.partner_id
        amount_total = self.amount_total
        partner_debit = partner.debit
        partner_debit_limit = partner.debit_limit
        notification_type = partner.notification_type
        notification_message = partner.notification_message

        payable = partner_debit + amount_total
        if notification_type == 'vendor_bill' and payable > partner_debit_limit:
            raise UserError(_(notification_message))

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for move in self:
            move.vendor_check_limit()
        return res