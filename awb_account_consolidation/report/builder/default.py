from odoo.addons.account_consolidation.report.builder.default import DefaultBuilder

import logging


_logger = logging.getLogger(__name__)


class DefaultBuilder(DefaultBuilder):
    def _get_params(self, period_ids: list, options: dict, line_id: str = None) -> dict:
        params = super()._get_params(period_ids, options, line_id)
        params.update({
            'analytic_accounts': options.get('analytic_accounts'),
            'analytic_tags': options.get('analytic_tags'),
        })
        _logger.debug(f'Params: {params} {options}')
        return params

    def _compute_account_totals(self, account_id: int, **kwargs) -> list:
        totals = []
        line_total = 0
        JournalLine = self.env['consolidation.journal.line']
        JournalItem = self.env['account.move.line']

        analytic_accounts = kwargs.get('analytic_accounts', [])
        analytic_tags = kwargs.get('analytic_tags', [])

        # Computing columns
        for journal in self.journals:
            # Check if a journal line exists
            if len(analytic_accounts) or len(analytic_tags):
                domain = [('account_id', '=', account_id), ('journal_id', '=', journal.id)]
                journal_ids = JournalLine.search(domain).mapped('move_line_ids').mapped('id')

                domain = [('id', 'in', journal_ids)]
                if len(analytic_accounts):
                    domain.append(('analytic_account_id', 'in', analytic_accounts))

                if len(analytic_tags):
                    domain.append(('analytic_tag_ids', 'in', analytic_tags))

                groupby_res = JournalItem.read_group(domain, ['debit:sum', 'credit:sum', 'journal_id'], ['journal_id'])
                debit_total = groupby_res[0]['debit'] if len(groupby_res) > 0 else 0
                credit_total = groupby_res[0]['credit'] if len(groupby_res) > 0 else 0
                journal_total_balance = debit_total - credit_total
            else:

                domain = [('account_id', '=', account_id), ('journal_id', '=', journal.id)]
                groupby_res = JournalLine.read_group(domain, ['amount:sum', 'journal_id'], ['journal_id'])
                journal_total_balance = groupby_res[0]['amount'] if len(groupby_res) > 0 else 0

            # Update totals
            totals.append(journal_total_balance)
            line_total += journal_total_balance

        totals.append(line_total)
        return totals
