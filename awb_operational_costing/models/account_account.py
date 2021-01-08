# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    operational_costing = fields.Boolean(string='Operational Costing')
