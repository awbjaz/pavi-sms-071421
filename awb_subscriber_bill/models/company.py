# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = "res.company"

    soa_logo = fields.Binary(string="SOA Logo")
    zone_code = fields.Char(string="Code")

    company_code = fields.One2many('company.code', 'company_id', string="Company Code")


class CompanyCode(models.Model):
    _name = "company.code"

    name = fields.Char(string="Code")
    count = fields.Integer(string="Count")
    is_active = fields.Boolean(string="Active", default=False)

    company_id = fields.Many2one('res.company', string="Company")

    @api.onchange('name')
    def _onchange_name(self):
        if self.name and len(self.name) != 4:
            raise UserError(_('Code must be 4 digit'))

    def _get_seq_count(self):
        self.write({"count": self.count + 1})
        return ("0000%s" % self.count)[-5:]

    def _update_active_code(self):
        max_count = 99_999
        if self.count >= max_count:
            new_code = self.company_id.company_code.filtered(
                lambda code:
                code.is_active == False
                and code.count < max_count
            )
            if new_code.exists():
                new_code = new_code[0]
                new_code.is_active = True
                self.is_active = False

    @api.model
    def create(self, vals):
        codes = self.search([
            ("company_id", "=", vals.get('company_id'))
        ])
        if len(codes) < 1:
            vals['is_active'] = True
        res = super(CompanyCode, self).create(vals)
        return res
