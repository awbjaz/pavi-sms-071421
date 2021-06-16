from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _description = "Purchase Order"

    def vendor_check_limit(self):
        partner = self.partner_id
        notification_type = partner.notification_type
        # Skip checking if not enabled
        if not partner.check_limit and notification_type == 'purchase_order':
            return

        amount_total = self.amount_total
        partner_debit = partner.debit
        partner_debit_limit = partner.debit_limit
        notification_message = partner.notification_message

        payable = partner_debit + amount_total
        if payable > partner_debit_limit:
            raise UserError(_(notification_message))

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            order.vendor_check_limit()
        return res
