# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from odoo import api, fields, models, _


class ProductTemplateExt(models.Model):
    _inherit = 'product.template'
    _description = 'Product Template'

    internet_usage = fields.Float(string="Internet Usage", required=True)