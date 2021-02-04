# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models, _


class CRMLead(models.Model):
    _inherit = "crm.lead"

    region_id = fields.Many2one('res.region', 'Region', domain="[('country_id', '=', country_id)]")

    @api.onchange('partner_id')
    def _onchange_customer(self):
        self.region_id = self.partner_id.region_id.id
