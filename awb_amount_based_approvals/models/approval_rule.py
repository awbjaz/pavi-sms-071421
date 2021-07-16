# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ApprovalRule(models.Model):
    _name = 'approval.rule'
    _description = 'Approval Rules'

    name = fields.Char('Name', required=True, index=True,
                       copy=False, compute='_compute_name')
    category = fields.Many2one('approval.category', String='Category')
    currency = fields.Many2one('res.currency', String='Currency')
    min_amount = fields.Float('Minimum Amount', required=True, tracking=True)
    max_amount = fields.Float('Maximum Amount', required=True, tracking=True)
    active = fields.Boolean('Active', index=True, default=True, tracking=True)
    approval_type = fields.Selection([('amount', 'Amount'),('none','None')], string='Approval Type', default='amount', tracking=True)
    department = fields.Many2one('hr.department', String='Department')

    approver_ids = fields.One2many('approval.rule.line','approval_id', String='Approvers')

    @api.depends('min_amount', 'max_amount')
    def _compute_name(self):
        for rule in self:
            category_name = rule.category.name if rule.category.name else ''
            currency_name = rule.currency.name if rule.currency.name else ''
            rule.name = f'{category_name} Amount: {currency_name} {rule.min_amount} - {rule.max_amount}'

class ApprovalRuleLine(models.Model):
    _name = "approval.rule.line"
    _description = "Approval Rules Line"
    _order = "sequence asc, id asc"

    sequence = fields.Integer(string="Sequence", required=True, default=1)
    approval_condition = fields.Selection([('and', 'AND'), ('or', 'OR')], string='Condition', default='and')
    approved_by = fields.Many2many('res.users', string='Approved By')
    approval_id = fields.Many2one('approval.rule', String="Approval")
