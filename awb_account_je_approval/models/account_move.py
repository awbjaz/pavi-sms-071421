# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('reviewed', 'Reviewed'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')
    reviewed_by = fields.Many2one('res.users', string='Reviewed By',
                                  copy=False, tracking=True, readonly=True)
    approved_by = fields.Many2one('res.users', string='Approved By',
                                  copy=False, tracking=True, readonly=True)

    @api.model
    def default_get(self, default_fields):
        # OVERRIDE
        values = super(AccountMove, self).default_get(default_fields)
        values['to_check'] = True

        return values

    def action_approve(self):
        self.reviewed_by = self.env.user.id
        self.state = 'reviewed'

    def action_post(self):
        super(AccountMove, self).action_post()
        self.approved_by = self.env.user.id

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMove, self).create(vals_list)
        for rec in res:
            if rec.type == 'entry':
                _logger.debug(f'Type {rec.type}')
                if rec.journal_id.type == 'general':
                    if not rec.line_ids:
                        raise UserError(_('Journal Items must have at least 1 record'))
        return res

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        _logger.debug(f'RESULT {res}')
        for rec in self:
            if rec.type == 'entry':
                if rec.journal_id.type == 'general':
                    if len(rec.line_ids) == 0:
                        raise UserError(_('Journal Items must have at least 1 record'))
        return res
