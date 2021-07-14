# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models
from odoo.exceptions import Warning, UserError, ValidationError


class PrPurchaseOrder(models.Model):
    _inherit = "purchase.order"

    approval_id = fields.Many2one(
        'approval.request', string="Approval Request")

    discount = fields.Float(string="Discount")
