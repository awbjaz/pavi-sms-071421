# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models


class AssetSell(models.TransientModel):
   _inherit = "account.asset.sell"

   invoice_id = fields.Many2one('account.move', string="Customer Invoice", help="The disposal invoice is needed in order to generate the closing journal entry.", domain="[('type', '=', 'out_invoice'), ('state', '=', 'posted'), ('asset_id','=', asset_id)]")
   