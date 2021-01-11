from odoo import api, fields, models, _


class AccountMoveLineExt(models.Model):
    _inherit = "account.move.line"
    _description = "Account Move Line"

    cost_allocation_id = fields.Many2one('cost.allocation', string="Cost Allocation ID")
    values = fields.Float(string="Values")
    share = fields.Float(string="Share")