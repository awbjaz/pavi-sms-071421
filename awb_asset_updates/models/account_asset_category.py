from odoo import api, fields, models, _


class AccountAssetCategory(models.Model):
    _name = 'account.asset.category'
    _description = 'Account Asset Category'

    name = fields.Char(string="Name")
    description = fields.Text(string="Description")
    asset_id = fields.One2many('account.asset', 'asset_category_id', string="Assets")