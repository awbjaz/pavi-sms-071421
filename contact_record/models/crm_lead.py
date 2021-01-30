# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models, _


class CRMLead(models.Model):
    _inherit = "crm.lead"

    province_id = fields.Many2one('res.province', 'Province', domain="[('country_id', '=', country_id)]")

    @api.onchange('partner_id')
    def _onchange_customer(self):
        self.province_id = self.partner_id.province_id.id
