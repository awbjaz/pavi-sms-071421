# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.tools import format_date, float_compare

import logging

_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    subscriber_location_id = fields.Many2one(
        related="partner_id.subscriber_location_id", string='Location')

    def _prepare_invoice_data(self):
        res = super(SaleSubscription, self)._prepare_invoice_data()
        due_day = self.subscriber_location_id.billing_due_day
        posting_day = self.subscriber_location_id.posting_day
        next_date = self.recurring_next_date

        if not next_date:
            raise UserError(_('Please define Date of Next Invoice of "%s".') % (self.display_name,))

        _logger.debug(f'Compute next date: Next {next_date}, due_day: {due_day}')

        recurring_next_date = self._get_recurring_next_date(self.recurring_rule_type, self.recurring_interval, next_date, due_day)
        end_date = fields.Date.from_string(recurring_next_date)
        recurring_posting_date = self._get_recurring_next_date(self.recurring_rule_type, self.recurring_interval, next_date, posting_day)
        posting_date = fields.Date.from_string(recurring_posting_date)

        narration = _("This invoice covers the following period: %s - %s") % (format_date(self.env, next_date), format_date(self.env, end_date))
        if self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms') and self.company_id.invoice_terms:
            narration += '\n' + self.company_id.invoice_terms

        res['start_date'] = recurring_next_date
        res['end_date'] = end_date
        res['posting_date'] = posting_date
        res['invoice_date_due'] = end_date
        res['narration'] = narration

        _logger.debug(f'RESULT {res}')
        return res
