from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class AccountAsset(models.Model):
    _inherit = 'account.asset'
    _description = 'Asset/Revenue Recognition'

    asset_number = fields.Char(string="Asset Reference")
    asset_category_id = fields.Many2one('account.asset.category', string="Asset Category")

    def validate(self):
        account_reference = self.env['ir.sequence'].next_by_code('account.asset.sequence.code')
        self.write({"asset_number": account_reference, 'asset_type': 'purchase'})
        return super(AccountAsset, self).validate()

    def name_get(self):
        data = []
        for rec in self:
            asset_number = rec.asset_number
            name = rec.name
            display_value = f"[{asset_number}] {name}"
            data.append((rec.id, display_value))
        return data