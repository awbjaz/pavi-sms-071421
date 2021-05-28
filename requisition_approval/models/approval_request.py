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

    def _default_application(self):
        _logger.debug(f'Default Application: {self._context} {self.has_application}: {self.category_id.application_type}')
        category_id = self._context.get('default_category_id', None)
        application = 'no'
        if category_id:
            category = self.env['approval.category'].browse(category_id)
            if category.has_application == 'default':
                application = category.application_type
            else:
                application = 'no'
        return application

    reference_number = fields.Char('Reference #', readonly=True)
    has_products = fields.Selection(related="category_id.has_products")
    has_application = fields.Selection(related="category_id.has_application")
    has_analytic_account = fields.Selection(related="category_id.has_analytic_account")
    company_id = fields.Many2one('res.company', string="Company", required=True, readonly=True, default=lambda self: self.env.company)

    product_line_ids = fields.One2many(
        'approval.product.line', 'approval_id', string="Products")

    application = fields.Selection(
        [('no', 'None')], default=_default_application, string="Application")

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

    def _compute_request_status(self):
        super(AwbApprovalRequest, self)._compute_request_status()
        for request in self:
            if request.request_status == 'approved':
                self.process_request_approval(request)

    def process_request_approval(self, request):
        # create place holder method
        return


class AwbApprovalProductLine(models.Model):
    _name = "approval.product.line"

    product_id = fields.Many2one(
        'product.product', string="Product", required=True)
    product_description = fields.Char(string="Description", required=True)
    quantity = fields.Float(string="Quantity", required=True, default=1)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure", required=True, domain="[('category_id', '=', product_uom_category_id)]")

    approval_id = fields.Many2one('approval.request')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.product_description = rec.product_id.name
                rec.uom_id = rec.product_id.uom_po_id.id
