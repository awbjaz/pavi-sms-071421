# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ApprovalType(models.Model):
    _inherit = 'approval.category'

    rule_ids = fields.Many2many('approval.rule', String='Rules')