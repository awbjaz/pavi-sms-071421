# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    subscriber_location_id = fields.Many2one('subscriber.location', string='Location')
    subscription_count = fields.Integer(related='subscriber_location_id.subscription_count',string="Number of Subscription")
    zone_type = fields.Selection([('vista', 'Vista'),
                                  ('non-vista', 'Non-Vista')], string='Zone Type')
    brand = fields.Many2one('zone.subtype', string='Brand')
