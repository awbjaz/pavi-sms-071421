# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models, _


class City(models.Model):
    _inherit = "res.city"

    state_id = fields.Many2one('res.country.state', 'Province', domain="[('country_id', '=', country_id)]")
