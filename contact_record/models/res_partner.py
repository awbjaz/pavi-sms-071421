# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    region_id = fields.Many2one('res.region', string='Region', ondelete='restrict', required=True, domain="[('country_id', '=?', country_id)]")
    state_id = fields.Many2one("res.country.state",
                               string='State',
                               ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    city_id = fields.Many2one('res.city',
                              string='City of Address',
                              domain="[('country_id', '=?', country_id)]")
    accredited = fields.Boolean(string='Accredited')
    validated = fields.Boolean(string='Validated')

    @api.onchange('city_id')
    def _onchange_city(self):
        if self.city_id.state_id:
            self.state_id = self.city_id.state_id

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.region_id.country_id:
            self.region_id = False

        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id and self.state_id != self.city_id.state_id:
            self.city_id = False

        if self.state_id.country_id:
            self.country_id = self.state_id.country_id

        if self.state_id.region_id:
            self.region_id = self.state_id.region_id

    @api.onchange('region_id')
    def _onchange_region(self):
        if self.region_id and self.region_id != self.state_id.region_id:
            self.state_id = False

        if self.region_id.country_id:
            self.country_id = self.region_id.country_id
