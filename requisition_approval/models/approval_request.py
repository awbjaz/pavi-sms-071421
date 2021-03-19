# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models
from odoo.exceptions import Warning, UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class AwbApprovalRequest(models.Model):
    _inherit = "approval.request"

    reference_number = fields.Char('Reference #', readonly=True)
    has_products = fields.Selection(related="category_id.has_products")
    has_application = fields.Selection(related="category_id.has_application")
    has_analytic_account = fields.Selection(related="category_id.has_analytic_account")

    product_line_ids = fields.One2many(
        'approval.product.line', 'approval_id', string="Products")

    application = fields.Selection(
        [('no', 'None')], default="no", string="Application")

    account_analytic_id = fields.Many2one(
                    'account.analytic.account', string="Analytic Account")

    def action_confirm(self):
        res = super(AwbApprovalRequest, self).action_confirm()
        if self.has_products == 'required' and not self.product_line_ids:
            raise UserError(
                "You have to add at least 1 products to confirm your request.")

        return res

    def _create(self, values):
        res = super(AwbApprovalRequest, self)._create(values)
        if res.category_id.prefix:
            res.reference_number = f'{res.category_id.prefix}-{res.id:06}'
            res.name += f' ({res.reference_number})'
        _logger.debug(res)

        return res


class AwbApprovalProductLine(models.Model):
    _name = "approval.product.line"

    product_id = fields.Many2one(
        'product.product', string="Product", required=True)
    product_description = fields.Char(string="Description", required=True)
    quantity = fields.Float(string="Quantity", required=True)
    uom_id = fields.Many2one(
        'uom.uom', string="Unit of Measure", required=True)

    approval_id = fields.Many2one('approval.request')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.product_description = rec.product_id.name
                rec.uom_id = rec.product_id.uom_po_id.id
