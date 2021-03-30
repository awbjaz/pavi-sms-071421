# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import logging


_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    state = fields.Selection(selection_add=[('for_approval', 'For Approval')])
    requested_by = fields.Many2one('res.partner', default=lambda self: self.env.user.partner_id.id, required=True)
    reviewed_by = fields.Many2one('res.partner')
    approval_lines = fields.One2many('purchase.order.approval.line', 'order_id',
                                     string='Approval Lines', tracking=True, copy=True)
    can_approve = fields.Boolean(string='My Approval',
                                 compute='_compute_can_approve',
                                 search='_search_for_approval',
                                 default=False)

    index_seq = fields.Integer(string='Index Sequence', default=1)

    def action_for_approval(self):
        self.state = 'for_approval'
        args = [('active', '=', True),
                ('min_amount', '<=', self.amount_total),
                ('max_amount', '>', self.amount_total),
                ]
        approval_rule = self.env['purchase.order.approval'].search(args, limit=1)

        approvers = []
        for record in approval_rule.approver_ids:
            for approver in record.approved_by:
                data = {
                    'rule_id': approval_rule.id,
                    'approval_condition': record.approval_condition,
                    'sequence': record.sequence,
                    'approver_id': approver.id
                }
                approvers.append((0, 0, data))

        self.sudo().update({'approval_lines': [(5, 0, 0)]})
        self.sudo().update({'approval_lines': approvers})

    def action_approve(self):
        is_approved = False
        is_validate = False
        approval_condition = 'and'
        approval_status = []
        approvers = []
        args = [('state', '=', 'pending'),
                ('order_id', '=', self.id),
                ('sequence', '=', self.index_seq)]

        approval_line_data = self.env['purchase.order.approval.line'].search(args)

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
            self.state = 'sent'
            self.reviewed_by = self.env.user.partner_id.id
            self.button_confirm()

    def action_reject(self):
        for approval in self.approval_lines:
            approver = approval.approver_id.id
            if approver == self.env.user.id:
                approval.sudo().update({'state': 'rejected'})
        self.sudo().update({'state': 'draft'})

    @api.depends('state')
    def _compute_can_approve(self):
        for po in self:
            if self.env.is_superuser():
                po.sudo().update({'can_approve': True})
            else:
                po.sudo().update({'can_approve': False})
                if po.state == 'for_approval':
                    can_approve = False
                    args = [('state', '=', 'pending'),
                            ('order_id', '=', po.id),
                            ('sequence', '=', po.index_seq)]

                    approval_line_data = self.env['purchase.order.approval.line'].search(args)

                    for approval in approval_line_data:
                        approver = approval.approver_id.id
                        _logger.debug(f'_compute_can_approve: {approver} {approval.state}')
                        if approver == self.env.user.id and approval.state == 'pending':
                            can_approve = True

                    if can_approve:
                        po.sudo().update({'can_approve': True})

    def _search_for_approval(self, operator, value):
        if operator not in ['=', '!='] or not isinstance(value, bool):
            raise UserError(_('Operation not supported'))
        if operator != '=':
            value = not value
        self._cr.execute(f"""
            SELECT id FROM purchase_order po
            WHERE EXISTS (SELECT * FROM purchase_order_approval_line po_app_line
                          WHERE po_app_line.order_id = po.id
                          AND po_app_line.approver_id = {self.env.user.id} LIMIT 1)
        """)
        return [('id', 'in' if value else 'not in', [r[0] for r in self._cr.fetchall()])]
