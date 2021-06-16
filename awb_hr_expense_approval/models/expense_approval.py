# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _


class HRExpenseApproval(models.Model):
    _name = "hr.expense.approval"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "HR Expense Approval"

    name = fields.Char('Name', required=True, index=True,
                       copy=False, compute='_compute_name')
    min_amount = fields.Float('Minimum Amount', required=True, tracking=True)
    max_amount = fields.Float('Maximum Amount', required=True, tracking=True)
    active = fields.Boolean('Active', index=True, default=True, tracking=True)
    approval_type = fields.Selection([('amount', 'Amount')], string='Approval Type', default='amount', tracking=True)
    employee_manager = fields.Boolean(string="Employee's Manager")
    department_manager = fields.Boolean(string="Department's Manager")

    approver_ids = fields.One2many('hr.expense.approver.line', 'approval_id', string='Approvers')
    company_id = fields.Many2one('res.company', 'Company', index=True, default=lambda self: self.env.company)

    @api.depends('min_amount', 'max_amount')
    def _compute_name(self):
        for rule in self:
            rule.name = f'{rule.min_amount} - {rule.max_amount}'


class HRExpenseApproverLine(models.Model):
    _name = "hr.expense.approver.line"
    _description = "Expense Approver Line"
    _order = "sequence asc, id asc"

    sequence = fields.Integer(string="Sequence", required=True, default=1)
    approval_condition = fields.Selection([('and', 'AND'), ('or', 'OR')], string='Condition', default='and')
    approved_by = fields.Many2many('res.users', string='Approved By')

    approval_id = fields.Many2one('hr.expense.approval', String="Approval")


class HRExpenseApprovalLine(models.Model):
    _name = "hr.expense.approval.line"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Expense Approval Line"

    expense_id = fields.Many2one('hr.expense.sheet', string='Expense Reference', index=True, required=True, ondelete='cascade')
    rule_id = fields.Many2one('hr.expense.approval', string="Rule", index=True)
    sequence = fields.Integer(string="Sequence", required=True)
    approval_condition = fields.Selection([('and', 'AND'), ('or', 'OR')], string='Condition', default='and')
    can_proceed = fields.Boolean(string="Can Proceed")
    approver_id = fields.Many2one('res.users', string="Approver", index=True, required=True, tracking=True)
    state = fields.Selection([('pending', 'Waiting'),
                              ('approved', 'Approved'),
                              ('rejected', 'Rejected')], default='pending', string="State", tracking=True)
    remarks = fields.Text('Reason', tracking=True)
