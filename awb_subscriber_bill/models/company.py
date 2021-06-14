# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models


class Company(models.Model):
    _inherit = "res.company"

    soa_logo = fields.Binary(string="SOA Logo")
    zone_code = fields.Char(string="Code")
