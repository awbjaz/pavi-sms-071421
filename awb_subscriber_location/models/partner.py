# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models


class ZoneSubType(models.Model):
    _name = 'zone.subtype'
    _description = 'Zone Subtype'

    name = fields.Char('Name', required=True)
    zone_type = fields.Selection([('vista', 'Vista'),
                                  ('non-vista', 'Non-Vista')], string='Zone Type')
    description = fields.Text('Description')


class Partner(models.Model):
    _inherit = "res.partner"

    subscriber_location_id = fields.Many2one('subscriber.location', domain=[('location_type', '=', 'zone')], string="Zone")
    category = fields.Selection(related='subscriber_location_id.category', string="Category")
