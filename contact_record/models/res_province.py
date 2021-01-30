# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
from odoo import api, fields, models, _

class Province(models.Model):
    _name = "res.province"

    name = fields.Char(string='Province', required=True)
    country_id = fields.Many2one('res.country', string="Country", required=True)
    region_id = fields.Many2one('res.country.state', string="Region", required=True)
