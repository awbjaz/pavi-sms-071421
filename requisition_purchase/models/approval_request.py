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


class PrApprovalRequest(models.Model):
    _inherit = "approval.request"

    has_warehouse = fields.Selection(related="category_id.has_warehouse")
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    picking_type_id = fields.Many2one(
        'stock.picking.type', string="Deliver To")

    purchase_process = fields.Selection([('product', 'Based on Product'),
                                         ('draft_po', 'Draft Purchase Order'),
                                         ('draft_pa', 'Draft Purchase Agreement')],
                                        string='Process')
    application = fields.Selection(
        selection_add=[('purchase', 'Purchase')])

    purchase_ids = fields.One2many(
        'purchase.order', 'approval_id', string="Purchase")

    purchase_requisition_ids = fields.One2many(
        'purchase.requisition', 'approval_id', string="Purchase")

    purchase_count = fields.Integer(
        string='Purchase Count', compute="_compute_purchase_count")

    purchase_requisition_count = fields.Integer(
        string='Purchase Count', compute="_compute_purchase_count")

    @api.model
    def _get_picking_type(self, warehouse_id):
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming'), ('warehouse_id', '=', warehouse_id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'incoming'), ('warehouse_id', '=', False)])
        return picking_type[:1]

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        p_type = self.picking_type_id
        if not(p_type and p_type.code == 'incoming' and (p_type.warehouse_id == self.warehouse_id or not p_type.warehouse_id)):
            self.picking_type_id = self._get_picking_type(self.warehouse_id.id)

    @api.depends('purchase_ids', 'purchase_requisition_ids')
    def _compute_purchase_count(self):
        for rec in self:
            rec.purchase_count = len(rec.purchase_ids)
            rec.purchase_requisition_count = len(rec.purchase_requisition_ids)

    def action_view_purchase(self):
        purchased = self.mapped('purchase_ids')
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        if len(purchased) > 1:
            action['domain'] = [('id', 'in', purchased.ids)]
        elif len(purchased) == 1:
            form_view = [
                (self.env.ref('purchase.purchase_order_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                    [(state, view)
                     for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = purchased.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action

    def action_view_purchase_requisition(self):
        requisition = self.mapped('purchase_requisition_ids')
        action = self.env.ref(
            'purchase_requisition.action_purchase_requisition').read()[0]
        if len(requisition) > 1:
            action['domain'] = [('id', 'in', requisition.ids)]
        elif len(requisition) == 1:
            form_view = [
                (self.env.ref('purchase_requisition.view_purchase_requisition_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                    [(state, view)
                     for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = requisition.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action

    def _create_purchase_order(self, line):
        # deprecated marked for removal
        purchase_data = {
            'partner_id': line.product_id.seller_ids[0].name.id if line.product_id.seller_ids else self.partner_id.id,
            'order_line': [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.product_description,
                'product_qty': line.quantity,
                'price_unit': line.product_id.list_price,
                'date_planned': fields.Datetime.now(),
                'product_uom': line.uom_id.id,
            })],

            'picking_type_id': self.picking_type_id.id,
            'approval_id': self.id,
            'origin': self.reference_number,
        }

        pocreate = self.purchase_ids.create(purchase_data)
        pocreate.message_post_with_view('mail.message_origin_link',
                                        values={
                                            'self': pocreate, 'origin': self},
                                        subtype_id=self.env.ref('mail.mt_note').id)

    def _create_purchase_requisition(self, line):
        # deprecated marked for removal
        tender_data = {
            'vendor_id': line.product_id.seller_ids[0].name.id if line.product_id.seller_ids else self.partner_id.id,
            'line_ids': [(0, 0, {
                'product_id': line.product_id.id,
                'product_qty': line.quantity,
                'price_unit': line.product_id.list_price,
                'product_uom_id': line.uom_id.id,
            })],
            'approval_id': self.id,
            'origin': self.reference_number,
        }

        tendercreate = self.purchase_requisition_ids.create(tender_data)
        tendercreate.message_post_with_view('mail.message_origin_link',
                                            values={
                                                'self': tendercreate, 'origin': self},
                                            subtype_id=self.env.ref('mail.mt_note').id)

    # 1. declare transactions = {"<types>": {"<vendor>": ["products"]}}
    # 2. loop through products
    #     if type not in transactions:
    #        transactions[type] = {}

    #     if vendor not in transactions[type]:
    #         transactions[type][vendor] = []

    #     transactions[type][vendor].append(product)

    # 3. loop through transactions create the related forms

    def _create_rfq(self, vendor, lines):
        order_line = []
        for line in lines:
            product = {
                'product_id': line.product_id.id,
                'name': line.product_description,
                'product_qty': line.quantity,
                'price_unit': line.product_id.list_price,
                'date_planned': fields.Datetime.now(),
                'product_uom': line.uom_id.id,
            }
            if self.account_analytic_id:
                product['account_analytic_id'] = self.account_analytic_id.id

            order_line.append((0, 0, product))

        purchase_data = {
            'partner_id': vendor,
            'order_line': order_line,
            'picking_type_id': self.picking_type_id.id,
            'approval_id': self.id,
            'origin': self.reference_number,
            'discount': 0
        }

        _logger.debug(f'User: {self.env.ref("base.user_root")}')

        pocreate = self.with_user(self.env.ref('base.user_root')).purchase_ids.create(purchase_data)
        pocreate.message_post_with_view('mail.message_origin_link',
                                        values={
                                            'self': pocreate, 'origin': self},
                                        subtype_id=self.env.ref('mail.mt_note').id)

    def _create_tenders(self, vendor, lines):
        order_line = []
        for line in lines:
            product = {
                'product_id': line.product_id.id,
                'product_qty': line.quantity,
                'price_unit': line.product_id.list_price,
                'product_uom_id': line.uom_id.id,
            }
            if self.account_analytic_id:
                product['account_analytic_id'] = self.account_analytic_id.id
            order_line.append((0, 0, product))

        tender_data = {
            'vendor_id': vendor,
            'line_ids': order_line,
            'approval_id': self.id,
            'origin': self.reference_number,
        }
        _logger.debug(f'User 2: {self.env.ref("base.user_root")}')

        tendercreate = self.with_user(self.env.ref('base.user_root')).purchase_requisition_ids.create(tender_data)
        tendercreate.message_post_with_view('mail.message_origin_link',
                                            values={
                                                'self': tendercreate, 'origin': self},
                                            subtype_id=self.env.ref('mail.mt_note').id)

    def process_request_approval(self, request):
        super(PrApprovalRequest, self).process_request_approval(request)
        transactions = {}
        if request.product_line_ids and request.application == 'purchase':
            for line in request.product_line_ids:
                if request.purchase_process == 'product':
                    requisition_type = line.product_id.purchase_requisition
                elif request.purchase_process == 'draft_po':
                    requisition_type = 'rfq'
                elif request.purchase_process == 'draft_pa':
                    requisition_type = 'tenders'

                if requisition_type not in transactions:
                    transactions[requisition_type] = {}

                vendor = line.product_id.seller_ids[0].name.id if line.product_id.seller_ids else self.partner_id.id
                if vendor not in transactions[requisition_type]:
                    transactions[requisition_type][vendor] = []

                transactions[requisition_type][vendor].append(line)

            for requisition_type in transactions:
                if requisition_type == 'rfq':
                    _logger.debug(
                        f'Requisition Type: {transactions[requisition_type]}')

                    for vendor in transactions[requisition_type]:
                        _logger.debug(
                            f'Vendor: {transactions[requisition_type][vendor]}')
                        lines = transactions[requisition_type][vendor]
                        self._create_rfq(vendor, lines)

                elif requisition_type == 'tenders':
                    for vendor in transactions[requisition_type]:
                        lines = transactions[requisition_type][vendor]
                        self._create_tenders(vendor, lines)
