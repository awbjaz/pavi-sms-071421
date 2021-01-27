# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    subscriber_location_id = fields.Many2one(related="partner_id.subscriber_location_id", string='Location')
