# -*- coding: utf-8 -*-
from odoo import fields, models


CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('no', 'None')]


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    has_stock_location = fields.Selection(
        CATEGORY_SELECTION, string="Has Stock Location", default="no", required=True,
        help="Stock Location that should be specified on the request.")
