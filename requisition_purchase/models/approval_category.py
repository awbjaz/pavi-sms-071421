# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models
from odoo.exceptions import Warning, UserError, ValidationError


class PrApprovalCategory(models.Model):
    _inherit = "approval.category"

    has_warehouse = fields.Selection([('required', 'Required'),
                                      ('no', 'None')], default='no', string="Warehouse", required=True)
    application_type = fields.Selection(
        selection_add=[('purchase', 'Purchase')])
