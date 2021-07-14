# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models


class Account(models.Model):
   _inherit = "account.move"

   for_asset_selling = fields.Boolean('For Asset Selling')
