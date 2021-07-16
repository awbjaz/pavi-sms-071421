# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ApprovalRequestDepartment(models.Model):
    _inherit = 'hr.department'

    operation_head = fields.Many2one('hr.employee', String='Operations Head')