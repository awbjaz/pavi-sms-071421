# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    subscriber_location_id = fields.Many2one('subscriber.location', string='Location')
