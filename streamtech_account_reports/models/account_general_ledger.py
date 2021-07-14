# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _

import logging


_logger = logging.getLogger(__name__)


class AccountGeneralLedgerReport(models.AbstractModel):
    _inherit = "account.general.ledger"
    _description = "General Ledger Report"

    @api.model
    def _get_columns_name(self, options):
        columns = super(AccountGeneralLedgerReport, self)._get_columns_name(options)
        columns.insert(2, {'name': _('Journal')})
        return columns

    @api.model
    def _get_account_title_line(self, options, account, amount_currency, debit, credit, balance, has_lines):
        res = super(AccountGeneralLedgerReport, self)._get_account_title_line(options, account, amount_currency, debit, credit, balance, has_lines)
        res['colspan'] = 5
        return res

    @api.model
    def _get_initial_balance_line(self, options, account, amount_currency, debit, credit, balance):
        res = super(AccountGeneralLedgerReport, self)._get_initial_balance_line(options, account, amount_currency, debit, credit, balance)
        res['colspan'] = 5
        return res

    @api.model
    def _get_aml_line(self, options, account, aml, cumulated_balance):
        _logger.debug(f'AML: {aml}')
        res = super(AccountGeneralLedgerReport, self)._get_aml_line(options, account, aml, cumulated_balance)
        res['columns'].insert(1, {'name': aml['journal_name'], 'title': aml['journal_name'], 'class': 'whitespace_print'},)
        return res

    @api.model
    def _get_account_total_line(self, options, account, amount_currency, debit, credit, balance):
        res = super(AccountGeneralLedgerReport, self)._get_account_total_line(options, account, amount_currency, debit, credit, balance)
        res['colspan'] = 5
        return res

    @api.model
    def _get_total_line(self, options, debit, credit, balance):
        res = super(AccountGeneralLedgerReport, self)._get_total_line(options, debit, credit, balance)
        res['colspan'] = 6
        return res
