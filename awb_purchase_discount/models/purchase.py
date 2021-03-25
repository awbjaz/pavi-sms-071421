# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    discount = fields.Float(string='Discount', required=True)

    @api.depends('order_line.price_total', 'discount')
    def _amount_all(self):
        res = super(PurchaseOrder, self)._amount_all()
        for rec in self:
            if rec.discount > 0:
                rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.discount
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    gross_amount = fields.Float(string='Gross Price')
    discount = fields.Float(string='Discount')
    discount_percentage = fields.Float(string='Discount %')
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price', compute='_compute_price')

    @api.depends('gross_amount', 'discount', 'discount_percentage')
    def _compute_price(self):
        for line in self:
            if line.discount > 0:
                price = line.gross_amount - line.discount

            elif line.discount_percentage > 0:
                price = line.gross_amount - (line.gross_amount * (line.discount_percentage / 100))

            else:
                price = line.gross_amount

            line.update({
                'price_unit': price
            })

    @api.onchange('discount', 'discount_percentage')
    def _onchange_discount(self):
        for line in self:
            if line.discount_percentage > 0:
                line.discount = 0

