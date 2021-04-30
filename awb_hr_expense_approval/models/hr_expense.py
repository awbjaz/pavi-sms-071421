# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import Warning, UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    state = fields.Selection(selection_add=[('for_approval', 'For Approval')])
    approval_lines = fields.One2many('hr.expense.approval.line', 'expense_id',
                                     string='Approval Lines', tracking=True, copy=True)
    can_approve = fields.Boolean(compute='_compute_can_approve', default=False)
    index_seq = fields.Integer(string='Index Sequence', default=1)

    def _get_data_approvers(self, rule_id, condition, sequence, approver_id, add_seq=0):
        data = {
            'rule_id': rule_id,
            'approval_condition': condition,
            'sequence': sequence + add_seq,
            'approver_id': approver_id,
        }
        _logger.debug(f'data {data}')
        return data

    def action_for_approval(self):
        self.state = 'for_approval'
        args = [('active', '=', True),
                ('min_amount', '<=', self.total_amount),
                ('max_amount', '>', self.total_amount),]
        approval_rule = self.env['hr.expense.approval'].search(args, limit=1)

        approvers = []
        add_seq =  0
        if approval_rule.employee_manager:
            if self.user_id:
                data = self._get_data_approvers(approval_rule.id, 'or', 1, self.user_id.id)
                approvers.append((0, 0, data))
                add_seq = 1
            else: 
                raise UserError(_('You need to set First Approver Manager to proceed.'))

        if approval_rule.department_manager:
            if approval_rule.employee_manager:
                if self.department_id.manager_id.user_id:
                    data = self._get_data_approvers(approval_rule.id, 'and', 2, self.department_id.manager_id.user_id.id)
                    approvers.append((0, 0, data))
                else: 
                    raise UserError(_('You need to set Department Manager to proceed.'))

            else:
                if self.department_id.manager_id.user_id:
                    data = self._get_data_approvers(approval_rule.id, 'and', 1, self.department_id.manager_id.user_id.id)
                    approvers.append((0, 0, data))
                    add_seq = 1
                else: 
                    raise UserError(_('You need to set Department Manager to proceed.'))

        for record in approval_rule.approver_ids:
            for approver in record.approved_by:
                data = self._get_data_approvers(approval_rule.id, record.approval_condition, record.sequence, approver.id, add_seq=add_seq)
                approvers.append((0, 0, data))
                
        _logger.debug(f'APPROVERS {approvers}')
        self.sudo().update({'approval_lines': [(5, 0, 0)]})
        self.sudo().update({'approval_lines': approvers})


    def action_approve(self):
        is_approved = False
        is_validate = False
        approval_condition = 'and'
        approval_status = []
        approvers = []
        args = [('state', '=', 'pending'),
                ('expense_id', '=', self.id),
                ('sequence', '=', self.index_seq)]

        approval_line_data = self.env['hr.expense.approval.line'].search(args)

        for approval in approval_line_data:
            approver = approval.approver_id.id
            approvers.append(approver)
            if approver == self.env.user.id:
                approval_condition = approval.approval_condition
                approval.state = 'approved'
                approval.can_proceed = True
            approval_status.append(approval.state)

        if approval_condition == 'or':
            is_approved = True
            for rec in approval_line_data:
                rec.can_proceed = True

            is_validate = all([line.can_proceed == True for line in self.approval_lines])
            _logger.debug(f'IS APPROVED IN CONDITION: {is_approved}')
            
        elif approval_condition == 'and':
            is_approved = all([state == 'approved' for state in approval_status])
            is_validate = all([line.can_proceed == True for line in self.approval_lines])

        _logger.debug(f'IS APPROVED: {is_approved}')
        _logger.debug(f'IS APPROVED Status: {approval_status}')
        _logger.debug(f'IS APPROVED COnditon: {approval_condition}')
        _logger.debug(f'IS VALIDATED: {is_validate}')
        if is_approved:
            self.index_seq += 1

            if approval_line_data:
                is_approved = False
                approval_status.clear()

        if is_validate:
            # self.state = 'sent'
            # self.reviewed_by = self.env.user.partner_id.id
            self.approve_expense_sheets()

    def action_reject(self):
        for approval in self.approval_lines:
            approver = approval.approver_id.id
            if approver == self.env.user.id:
                approval.sudo().update({'state': 'rejected'})
        self.sudo().update({'state': 'submit'})

    @api.depends('state')
    def _compute_can_approve(self):
        if self.env.is_superuser():
            self.sudo().update({'can_approve': True})
        else:
            self.sudo().update({'can_approve': False})
            if self.state == 'for_approval':
                can_approve = False
                args = [('state', '=', 'pending'),
                        ('expense_id', '=', self.id),
                        ('sequence', '=', self.index_seq)]

                approval_line_data = self.env['hr.expense.approval.line'].search(args)

                for approval in approval_line_data:
                    approver = approval.approver_id.id
                    _logger.debug(f'_compute_can_approve: {approver} {approval.state}')
                    if approver == self.env.user.id and approval.state == 'pending':
                        can_approve = True

                if can_approve:
                    self.sudo().update({'can_approve': True})
