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
