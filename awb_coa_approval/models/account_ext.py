from odoo import api, fields, models, _

ACCOUNT_STATE = [
    ('draft', 'Draft'),
    ('for_approval', 'For Approval'),
    ('approved', 'Approved'),
    ('deprecated', 'Deprecated')]


class AccountAccount(models.Model):
    _inherit = "account.account"
    _description = "Account"

    state = fields.Selection(ACCOUNT_STATE, string="Status", default="draft")
    deprecated = fields.Boolean(index=True, default=True)

    def action_reset_to_draft(self):
        self.write({"state": "draft", "deprecated": True})

    def action_for_approval(self):
        self.write({"state": "for_approval", "deprecated": True})

    def action_approve(self):
        self.write({"state": "approved", "deprecated": False})

    def action_deprecated(self):
        self.write({"state": "deprecated", "deprecated": True})