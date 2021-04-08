# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.tools import format_date, float_compare
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    subscriber_location_id = fields.Many2one(
        related="partner_id.subscriber_location_id", string='Location')

    def _prepare_invoice_data(self):
        res = super(SaleSubscription, self)._prepare_invoice_data()
        if not self.subscriber_location_id:
            raise UserError(_('No Zone assigned to subscriber. Please update subscriber record.'))
        cutoff_day = self.subscriber_location_id.cutoff_day
        due_day = self.subscriber_location_id.billing_due_day
        posting_day = self.subscriber_location_id.posting_day
        next_date = self.recurring_next_date

        if not next_date:
            raise UserError(_('Please define Date of Next Invoice of "%s".') % (self.display_name,))

        periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
        interval_type = periods[self.recurring_rule_type]
        interval = self.recurring_interval

        if cutoff_day < 16:
            next_date = next_date - relativedelta(**{interval_type: interval})
        else:
            next_date = next_date - relativedelta(**{interval_type: interval*2})

        _logger.debug(f'Compute next date: Next {next_date}, due_day: {due_day}')
        recurring_start_date = self._get_recurring_next_date(self.recurring_rule_type, interval, next_date, cutoff_day)
        start_date = fields.Date.from_string(recurring_start_date+relativedelta(days=1))

        recurring_next_date = self._get_recurring_next_date(self.recurring_rule_type, 0, start_date, cutoff_day)
        recurring_posting_date = self._get_recurring_next_date(self.recurring_rule_type, 0, start_date, posting_day)
        recurring_due_date = self._get_recurring_next_date(self.recurring_rule_type, interval, start_date, due_day)
        _logger.debug(f'Days: {recurring_start_date >= recurring_next_date}: {recurring_start_date} > {recurring_next_date}')
        # This is a HACK to fix the issue with jumping dates
        if recurring_start_date >= recurring_next_date:
            recurring_next_date = self._get_recurring_next_date(self.recurring_rule_type, interval, start_date, cutoff_day)

        end_date = fields.Date.from_string(recurring_next_date)
        posting_date = fields.Date.from_string(recurring_posting_date)
        due_date = fields.Date.from_string(recurring_due_date)

        _logger.debug(f'Period Covered: {start_date}-{end_date}')

        narration = _("This invoice covers the following period: %s - %s") % (format_date(self.env, start_date), format_date(self.env, end_date))
        if self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms') and self.company_id.invoice_terms:
            narration += '\n' + self.company_id.invoice_terms

        res['start_date'] = start_date
        res['end_date'] = end_date
        res['posting_date'] = posting_date
        res['invoice_date_due'] = due_date
        res['narration'] = narration

        _logger.debug(f'RESULT {res}')
        return res
