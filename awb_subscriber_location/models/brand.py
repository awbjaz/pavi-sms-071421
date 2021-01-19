# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models


class ProjectBrand(models.Model):
    _name = "project.brand"
    _description = "Brand"

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
