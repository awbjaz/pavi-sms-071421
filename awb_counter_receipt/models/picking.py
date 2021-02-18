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
