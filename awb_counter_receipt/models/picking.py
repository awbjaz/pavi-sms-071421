# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = "stock.picking"

    si_num = fields.Char(string="SI Number")
    dr_num = fields.Char(string="DR Number")
    mrr_num = fields.Char(string="MRR Number")


    @api.onchange('si_num', 'dr_num', 'mrr_num')
    def _onchange_num(self):
        pick_no = {
                'si_num': '',
                'dr_num': '',
                'mrr_num': '',
            }
        if self.purchase_id:
            pick_no['si_num'] = self.si_num
            pick_no['dr_num'] = self.dr_num
            pick_no['mrr_num'] = self.mrr_num

        self.purchase_id.update(pick_no)
