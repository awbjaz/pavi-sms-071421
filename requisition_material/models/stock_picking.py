# -*- coding: utf-8 -*-

from odoo import models


class Picking(models.Model):
    _inherit = "stock.picking"

    def action_confirm(self):
        res = super(Picking, self).action_confirm()
        if self.picking_type_id.code == 'internal' and self.origin:
            approval = self.env['approval.request'].sudo().search([('reference_number', '=', self.origin)], limit=1)

            if approval:
                approval.message_post_with_view('requisition_material.message_transfer_link',
                                                values={'self': self, 'origin': self},
                                                subtype_id=self.env.ref('mail.mt_note').id)
        return res
