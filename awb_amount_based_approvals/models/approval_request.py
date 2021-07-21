# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    department_id = fields.Many2one('hr.department', String='Department')
    manager_id = fields.Many2one('hr.employee', String='Manager')

    @api.model
    def create(self, vals):
        
        data = []

        res = super(ApprovalRequest, self).create(vals)

        manager_id = res.mapped('manager_id').user_id.id
        head_id = res.mapped('department_id').operation_head.user_id.id

        rule_args = [
            ('category', '=', vals.get('category_id')),
            ('min_amount', '<=', vals.get('amount')),
            ('max_amount', '>=', vals.get('amount')),
        ]
        rule_id = self.env['approval.rule'].search(rule_args, limit=1)
        rule_approvers = rule_id.mapped('approver_ids')

        category_id = res.mapped('category_id').rule_ids.filtered(lambda x: x.id == rule_id.id)
        if category_id.manager_id:
            if manager_id:    
                manager_data = {
                        'user_id': manager_id,
                        'status': 'new',
                        'request_id': res.id,
                    }
                data.append(manager_data)
            else:
                raise UserError(_('No User Account Associated on this Manager.'))
        if category_id.operation_head_id:
            if head_id:
                head_data = {
                        'user_id': head_id,
                        'status': 'new',
                        'request_id': res.id,
                }
                data.append(head_data)
            else:
                raise UserError(_('No User Account Associated on this Operation Head.'))
        if rule_approvers:
            for approver in rule_approvers.approved_by:
                approver_data = {
                        'user_id': approver.id,
                        'status': 'new',
                        'request_id': res.id,
                }
                data.append(approver_data)
                
        if len(data) > 0:
            approvers = self.env['approval.approver']
            approvers.create(data)
            _logger.debug('Approvals Created!')
        return res

