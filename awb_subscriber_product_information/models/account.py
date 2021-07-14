
from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    customer_number = fields.Char(related='partner_id.customer_number')
