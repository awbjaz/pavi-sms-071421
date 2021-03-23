# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    application = fields.Selection(
        selection_add=[('warehouse', 'Inventory')])

    has_stock_location = fields.Selection(
        related="category_id.has_stock_location")
    location_id = fields.Many2one('stock.location', string="Source Stock Location",
                                  domain=[('usage', '=', 'internal')])
    location_dest_id = fields.Many2one('stock.location', string="Destination Stock Location",
                                       domain=[('usage', 'in', ['internal','customer'])])
    location_transit_id = fields.Many2one('stock.location', string="Transit Location",
                                          domain=[('usage', 'in', ['internal','transit'])])
    wh_picking_type_id = fields.Many2one('stock.picking.type', string="Inventory Operation",
                                      domain=[('code','in',['internal','outgoing'])])

    transfers_count = fields.Integer(
        string='Transfer Request Count', compute="_compute_transfer_request_count")
    
    @api.onchange('wh_picking_type_id')
    def onchange_picking_type_id(self):
        if self.wh_picking_type_id:
            self.location_id = self.wh_picking_type_id.default_location_src_id.id
            self.location_dest_id = self.wh_picking_type_id.default_location_dest_id.id
        
    def _compute_transfer_request_count(self):
        for rec in self:
            transfers = self.env['stock.picking'].sudo().search(
                [('origin', '=', rec.reference_number)])
            rec.transfers_count = len(transfers)

    def action_approve(self, approver=None):
        super(ApprovalRequest, self).action_approve(approver=None)
        if self.application == 'warehouse':
            picking = self.env['stock.picking'].sudo()
#             picking_type = self.env['stock.picking.type'].sudo().search(
#                 [('code', '=', 'internal')], limit=1)

            """Checking of related partner record"""
            if self.partner_id: partner_id = self.partner_id.id
            else: partner_id = self.request_owner_id.partner_id.id

            if not self.location_transit_id:
                products = []
                for product in self.product_line_ids:
                    item = {
                        'name': product.product_id.name,
                        'product_id': product.product_id.id,
                        'product_uom': product.uom_id.id,
                        'product_uom_qty': product.quantity
                    }
                    products.append((0, 0, item))

                data = {
                    'partner_id': partner_id,
                    'picking_type_id': self.wh_picking_type_id.id,
                    'user_id': self.request_owner_id.id,
                    'location_id': self.location_id.id,
                    'location_dest_id': self.location_dest_id.id,
                    'origin': self.reference_number,
                    'move_lines': products
                }

                transfer_request = picking.create(data)

                transfer_request.message_post_with_view('mail.message_origin_link',
                                                        values={
                                                            'self': transfer_request, 'origin': self},
                                                        subtype_id=self.env.ref('mail.mt_note').id)

            else:
                products = []
                for product in self.product_line_ids:
                    item = {
                        'name': product.product_id.name,
                        'product_id': product.product_id.id,
                        'product_uom': product.uom_id.id,
                        'product_uom_qty': product.quantity
                    }
                    products.append((0, 0, item))


                data_source_to_transit = {
                    'partner_id': partner_id,
                    'picking_type_id': self.picking_type_id.id,
                    'location_id': self.location_id.id,
                    'user_id': self.request_owner_id.id,
                    'location_dest_id': self.location_transit_id.id,
                    'origin': self.reference_number,
                    'move_lines': products
                }

                data_transit_to_destination = {
                    'partner_id': partner_id,
                    'picking_type_id': self.picking_type_id.id,
                    'location_id': self.location_transit_id.id,
                    'location_dest_id': self.location_dest_id.id,
                    'origin': self.reference_number,
                    'move_lines': products
                }

                source_to_transit = picking.create(data_source_to_transit)
                transit_to_destination = picking.create(data_transit_to_destination)

                source_to_transit.message_post_with_view('mail.message_origin_link',
                                                    values={
                                                        'self': source_to_transit, 'origin': self},
                                                    subtype_id=self.env.ref('mail.mt_note').id)

                transit_to_destination.message_post_with_view('mail.message_origin_link',
                                                    values={
                                                        'self': transit_to_destination, 'origin': self},
                                                    subtype_id=self.env.ref('mail.mt_note').id)


    def action_withdraw(self, approver=None):
        super(ApprovalRequest, self).action_withdraw(approver=None)
        if self.application == 'warehouse':
            picking = self.env['stock.picking'].sudo()
            picking_ids = picking.sudo().search([('origin','=',self.reference_number),
                                                 ('state','!=','done')])
            for rec in picking_ids:
                rec.state = 'cancel'
    
    def action_cancel(self):
        super(ApprovalRequest, self).action_cancel()
        if self.application == 'warehouse':
            picking = self.env['stock.picking'].sudo()
            picking_ids = picking.sudo().search([('origin','=',self.reference_number),
                                                 ('state','!=','done')])
            for rec in picking_ids:
                rec.state = 'cancel'
            

    def action_view_transfer_request(self):
        document = self.env['stock.picking'].sudo().search(
            [('origin', '=', self.reference_number)])
        action = self.env.ref(
            'stock.stock_picking_action_picking_type').read()[0]
        if len(document) > 1:
            action['domain'] = [('id', 'in', document.ids)]
        elif len(document) == 1:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                    [(state, view)
                     for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = document.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action
