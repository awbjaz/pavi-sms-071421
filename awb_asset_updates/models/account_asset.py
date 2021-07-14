from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class AccountAsset(models.Model):
    _inherit = 'account.asset'
    _description = 'Asset/Revenue Recognition'

    asset_number = fields.Char(string="Asset Reference")
    asset_category_id = fields.Many2one('account.asset.category', string="Asset Category")

    def validate(self):
        res = super(AccountAsset, self).validate()
        account_reference = self.env['ir.sequence'].next_by_code('account.asset.sequence.code')
        self.write({"asset_number": account_reference})
        return res

    def name_get(self):
        data = []
        for rec in self:
            asset_number = f"[{rec.asset_number}]" if rec.asset_number else ""
            name = rec.name
            display_value = f"{asset_number} {name}"
            data.append((rec.id, display_value))
        return data