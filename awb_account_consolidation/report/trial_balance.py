from odoo import models, api

from odoo.addons.account_consolidation.report.handler.journals import JournalsHandler
from odoo.addons.account_consolidation.report.builder.comparison import ComparisonBuilder
from .builder.default import DefaultBuilder


import logging


_logger = logging.getLogger(__name__)


class AccountConsolidationTrialBalanceReport(models.AbstractModel):
    _inherit = "account.consolidation.trial_balance_report"

    filter_analytic = True

    def _get_options(self, previous_options=None):
        _logger.debug(f'Previous options: {previous_options}')
        current_options = super()._get_options(previous_options)
        if 'analytic_accounts' not in current_options.keys():
            current_options['analytic_accounts'] = []
        if 'analytic_tags' not in current_options.keys():
            current_options['analytic_tags'] = []
        _logger.debug(f'Current options: {current_options}')
        return current_options

    @api.model
    def _get_lines(self, options, line_id=None):
        selected_aps = self._get_period_ids(options)
        selected_ap = self._get_selected_period()

        # comparison
        if len(selected_aps) > 1:
            builder = ComparisonBuilder(self.env, selected_ap._format_value)
        else:
            journal_ids = JournalsHandler.get_selected_values(options)
            journals = self.env['consolidation.journal'].browse(journal_ids)
            builder = DefaultBuilder(self.env, selected_ap._format_value, journals)
        return builder.get_lines(selected_aps, options, line_id)

    def action_open_audit(self, options, params=None):
        action = super().action_open_audit(options, params)

        analytic_accounts = options.get('analytic_accounts', [])
        analytic_tags = options.get('analytic_tags', [])

        if len(analytic_accounts):
            action['context'].update({'search_default_analytic_account_id': analytic_accounts})

        if len(analytic_tags):
            action['context'].update({'search_default_analytic_tag_ids': analytic_tags})

        _logger.debug(f'Open Audit Options: {options}, Action: {action}')
        return action
