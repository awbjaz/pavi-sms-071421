from odoo import api, fields, models, _
from logging import getLogger

_logger = getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    reviewed_by = fields.Many2one('res.users', string='Reviewed By',
                                  copy=False, tracking=True)
    approved_by = fields.Many2one('res.users', string='Approved By',
                                  copy=False, tracking=True)
    prepared_by = fields.Many2one('res.users', string='Prepared By',
                                  copy=False, tracking=True, default=lambda self: self.env.user.id)
    entered_by = fields.Many2one('res.users', string='Entered By',
                                 copy=False, tracking=True, default=lambda self: self.env.user.id)
    audited_by = fields.Many2one('res.users', string='Audited By',
                                 copy=False, tracking=True)
    posted_by = fields.Many2one('res.users', string='Posted By',
                                copy=False, tracking=True)
    received_by = fields.Many2one('res.users', string='Received By',
                                  copy=False, tracking=True)

    def action_approve(self):
        res = super(AccountMove, self).action_approve()
        self.posted_by = self.env.user.id
        return res

    def action_post(self):
        res = super(AccountMove, self).action_post()
        self.audited_by = self.env.user.id
        self.approved_by = self.env.user.id
        return res
