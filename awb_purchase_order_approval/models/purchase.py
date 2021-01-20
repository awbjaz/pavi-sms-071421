# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
import logging


_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    state = fields.Selection(selection_add=[('for_approval', 'For Approval')])
    requested_by = fields.Many2one('res.partner', default=lambda self: self.env.user.id)
    reviewed_by = fields.Many2one('res.partner')
    approval_lines = fields.One2many('purchase.order.approval.line', 'order_id', string='Approval Lines', tracking=True, readonly=True, copy=True)
    can_approve = fields.Boolean(compute='_compute_can_approve', default=False)

    def action_for_approval(self):
        self.state = 'for_approval'
        args = [('is_active', '=', True),
                ('min_amount', '<=', self.amount_total),
                ('max_amount', '>', self.amount_total),
                ]
        approval_rule = self.env['purchase.order.approval'].search(args, limit=1)
        approvers = []
        for approver in approval_rule.approved_by:
            data = {
                'rule_id': approval_rule.id,
                'approver_id': approver.id
            }
            approvers.append((0, 0, data))

        self.sudo().update({'approval_lines': [(5, 0, 0)]})
        self.sudo().update({'approval_lines': approvers})

    def action_approve(self):
        is_approved = False
        approvers = []
        approval_condition = 'and'
        approval_status = []
        for approval in self.approval_lines:
            approver = approval.approver_id.id
            approvers.append(approver)
            if approver == self.env.user.id:
                approval_condition = approval.rule_id.approval_condition
                approval.state = 'approved'
            approval_status.append(approval.state)

        if len(approvers) <= 1:
            is_approved = True
        else:
            if approval_condition == 'or':
                is_approved = True
            elif approval_condition == 'and':
                is_approved = all([state == 'approved' for state in approval_status])

        if is_approved:
            self.state = 'sent'
            self.reviewed_by = self.env.user.id
            self.button_confirm()

    def action_reject(self):
        for approval in self.approval_lines:
            approver = approval.approver_id.id
            if approver == self.env.user.id:
                approval.state = 'approved'
        self.sudo().update({'state': 'draft'})

    @api.depends('state')
    def _compute_can_approve(self):
        if self.env.is_superuser():
            self.sudo().update({'can_approve': True})
        else:
            self.sudo().update({'can_approve': False})
            if self.state == 'for_approval':
                can_approve = False
                for approval in self.approval_lines:
                    approver = approval.approver_id.id
                    _logger.debug(f'{approver} {approval.state}')
                    if approver == self.env.user.id and approval.state == 'pending':
                        can_approve = True

                if can_approve:
                    self.sudo().update({'can_approve': True})
