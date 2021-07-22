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
        seq = 0

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
                seq += 1    
                manager_data = {
                        'user_id': manager_id,
                        'status': 'new',
                        'request_id': res.id,
                        'sequence': seq ,
                    }
                data.append(manager_data)
            else:
                raise UserError(_('No User Account Associated on this Manager.'))
        if category_id.operation_head_id:
            if head_id:
                seq += 1
                head_data = {
                        'user_id': head_id,
                        'status': 'new',
                        'request_id': res.id,
                        'sequence': seq ,
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

    @api.depends('approver_ids.status')
    def _compute_request_status(self):
        for request in self:
            status_lst = request.mapped('approver_ids.status')

            if status_lst:
                if status_lst.count('cancel'):
                    status = 'cancel'
                elif status_lst.count('refused'):
                    status = 'refused'
                elif status_lst.count('new') == len(status_lst):
                    status = 'new'
                elif status_lst.count('approved') == len(status_lst):
                    status = 'approved'
                else:
                    status = 'pending'
            else: 
                status = 'new'
            request.request_status = status

    def action_confirm(self):

        res = super(ApprovalRequest, self).action_confirm()
        request_approver = self.mapped('approver_ids')
        for record in request_approver:
            if record.sequence:
                approvers = request_approver.filtered(lambda approver: approver.sequence != 1)
                approvers.write({'status': 'new'})
        return res

    def action_approve(self):

        res = super(ApprovalRequest,self).action_approve()  
        approver = self.mapped('approver_ids')
        current_approver = approver.filtered(lambda approver: approver.user_id == self.env.user)
        next_approver = approver.filtered(lambda approver: approver.sequence == current_approver.sequence + 1)
        if next_approver:
            if next_approver.sequence:
                next_approver.write({'status': 'pending'})
      
        return res

class ApprovalApprover(models.Model):
    _inherit = 'approval.approver'

    sequence = fields.Integer(string='Sequence', default=1, readonly=True)
    approval_condition = fields.Selection([('and', 'AND'), ('or', 'OR')], string='Condition', default='and')
