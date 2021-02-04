# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
from odoo import api, fields, models, _

class Country(models.Model):
    _inherit = "res.country"

    region_ids = fields.One2many('res.region', 'country_id', string="Regions")
