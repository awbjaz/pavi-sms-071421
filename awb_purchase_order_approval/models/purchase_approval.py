# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _


class PurchaseOrderApproval(models.Model):
    _name = "purchase.order.approval"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Purchase Order Approval"

    name = fields.Char('Name', required=True, index=True,
                       copy=False, compute='_compute_name')
    min_amount = fields.Float('Minimum Amount', required=True, tracking=True)
    max_amount = fields.Float('Maximum Amount', required=True, tracking=True)
    active = fields.Boolean('Active', index=True, default=True, tracking=True)
    approval_type = fields.Selection([('amount', 'Amount')], string='Approval Type', default='amount', tracking=True)
   
    approver_ids = fields.One2many('purchase.order.approver.line', 'approval_id', string='Approvers')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    @api.depends('min_amount', 'max_amount')
    def _compute_name(self):
        for rule in self:
            rule.name = f'{rule.min_amount} - {rule.max_amount}'


class PurchaseOrderApprovalLine(models.Model):
    _name = "purchase.order.approval.line"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Purchase Order Approval Line"

    order_id = fields.Many2one('purchase.order', string='Order Reference', index=True, required=True, ondelete='cascade')
    rule_id = fields.Many2one('purchase.order.approval', string="Rule", index=True, required=True)
    sequence = fields.Integer(string="Sequence")
    approval_condition = fields.Selection([('and', 'AND'), ('or', 'OR')], string='Condition', default='and')
    can_proceed = fields.Boolean(string="Can Proceed")
    approver_id = fields.Many2one('res.users', string="Approver", index=True, required=True, tracking=True)
    state = fields.Selection([('pending', 'Waiting'),
                              ('approved', 'Approved'),
                              ('rejected', 'Rejected')], default='pending', string="State", tracking=True)
    remarks = fields.Text('Reason', tracking=True)
    approval_condition = fields.Selection([('and', 'AND'), ('or', 'OR')], string='Condition')


class PurchaseOrderApproverLine(models.Model):
    _name = "purchase.order.approver.line"
    _description = "Purchase Order Approver Line"
    _order = "sequence asc, id asc"

    sequence = fields.Integer(string="Sequence", default=1)
    approval_condition = fields.Selection([('and', 'AND'), ('or', 'OR')], string='Condition', default='and')
    approved_by = fields.Many2many('res.users', string='Approved By')

    approval_id = fields.Many2one('purchase.order.approval', String="Approval")
