# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    state = fields.Selection(selection_add=[('reviewed', 'Reviewed')])
    reviewed_by = fields.Many2one('res.users', string='Reviewed By',
                                  copy=False, tracking=True, readonly=True)
    approved_by = fields.Many2one('res.users', string='Approved By',
                                  copy=False, tracking=True, readonly=True)

    @api.model
    def default_get(self, default_fields):
        # OVERRIDE
        values = super(AccountMove, self).default_get(default_fields)
        values['to_check'] = True

        return values

    def action_approve(self):
        self.reviewed_by = self.env.user.id
        self.state = 'reviewed'

    def action_post(self):
        super(AccountMove, self).action_post()
        self.approved_by = self.env.user.id
