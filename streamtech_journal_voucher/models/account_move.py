from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    reviewed_by = fields.Many2one('res.users', string='Reviewed By',
                                  copy=False, tracking=True)
    approved_by = fields.Many2one('res.users', string='Approved By',
                                  copy=False, tracking=True)
