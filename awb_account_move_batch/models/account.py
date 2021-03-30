# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging


_logger = logging.getLogger(__name__)


class Account(models.Model):
    _inherit = "account.move"

    batch_rebates_id = fields.Many2one('account.move.batch', string="Batch Rebates", readonly=True)

    