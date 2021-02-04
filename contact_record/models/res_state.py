# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
from odoo import api, fields, models, _

class State(models.Model):
    _inherit = "res.country.state"

    region_id = fields.Many2one('res.region', string="Region", required=True)
