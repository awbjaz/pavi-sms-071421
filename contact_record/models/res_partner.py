# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    province_id = fields.Many2one('res.province','Province', domain="[('country_id', '=', country_id)]")
    city_id = fields.Many2one('res.city', string='City of Address', required=True)
    accredited = fields.Boolean(string='Accredited')
    validated = fields.Boolean(string='Validated')

    @api.onchange('city_id')
    def _onchange_city(self):
        if self.city_id:
            self.province_id = self.city_id.province_id
