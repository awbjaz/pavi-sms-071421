# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleSubscriptionTemplate(models.Model):
    _inherit = "sale.subscription.template"

    @api.onchange('recurring_rule_count')
    def _onchange_recurring_rule_count(self):
        for rec in self:
            if rec.recurring_rule_count < 0:
                raise UserError(_('You cannot enter a negative value'))
