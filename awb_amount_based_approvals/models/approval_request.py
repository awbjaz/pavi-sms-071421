# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    department_id = fields.Many2one('hr.department', String='Department')
    manager_id = fields.Many2one('hr.employee', String='Manager')

class ApprovalRequestDepartment(models.Model):
    _inherit = 'hr.department'

    operation_head = fields.Many2one('hr.employee', String='Operations Head')