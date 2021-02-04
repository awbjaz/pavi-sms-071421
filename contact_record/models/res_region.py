# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
from odoo import api, fields, models, _

class Region(models.Model):
    _name = "res.region"

    name = fields.Char(string='Region', required=True)
    country_id = fields.Many2one('res.country', string="Country", required=True)
    state_ids = fields.One2many('res.country.state', 'region_id', string="Provinces", required=True)
