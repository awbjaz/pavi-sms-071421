from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

NOTIFICATION_TYPE = [
    ('purchase_order', 'Purchase Order'),
    ('vendor_bill', 'Vendor Bill')]


class Partner(models.Model):
    _inherit = "res.partner"

    check_limit = fields.Boolean(string="Check Limit")
    notification_type = fields.Selection(NOTIFICATION_TYPE, string="Notification Type", default="purchase_order")
    notification_message = fields.Text(string="Notification Message", default="You've reached the credit limit for this vendor")