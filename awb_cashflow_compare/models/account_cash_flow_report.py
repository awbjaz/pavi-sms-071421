# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

from dateutil.relativedelta import relativedelta

import copy
import logging

_logger = logging.getLogger(__name__)


class AccountCashFlowReport(models.AbstractModel):
    _inherit = 'account.cash.flow.report'
    _description = 'Cash Flow Report'

    def _with_correct_filters(self):
        _logger.debug(f'test')
        self.comparison = True
        self.filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
        return self

    def get_report_informations(self, options):
        return super(AccountCashFlowReport, self._with_correct_filters()).get_report_informations(options)

    # -------------------------------------------------------------------------
    # COLUMNS / LINES
    # -------------------------------------------------------------------------\

    @api.model
    def _get_columns_name(self, options):
        columns = super(AccountCashFlowReport, self)._get_columns_name(options)
        if options.get('comparison') and options['comparison'].get('periods'):
            columns[1]['name'] = options['date']['string']
            for period in options['comparison']['periods']:
                columns.append({'name': period['string'], 'class': 'number'})

        return columns

    @api.model
    def _get_lines_to_compute(self, options):
        lines = super(AccountCashFlowReport, self)._get_lines_to_compute(options)
        if options.get('comparison') and options['comparison'].get('periods'):
            for line in lines:
                for period in options['comparison']['periods']:
                    line['columns'].append({'name': 0.0, 'class': 'number'})

        return lines

    @api.model
    def _get_lines(self, options, line_id=None):

        def _insert_at_index(index, account_id, account_code, account_name, amount, column=0):
            ''' Insert the amount in the right section depending the line's index and the account_id. '''
            # Helper used to add some values to the report line having the index passed as parameter
            # (see _get_lines_to_compute).
            line = lines_to_compute[index]

            if self.env.company.currency_id.is_zero(amount):
                return

            line.setdefault('unfolded_lines', {})
            columns_count = 1
            if options.get('comparison') and options['comparison'].get('periods'):
                columns_count += len(options['comparison'].get('periods'))

            columns = [{'name': 0.0, 'class': 'number'} for x in range(columns_count)]
            line['unfolded_lines'].setdefault(account_id, {
                'id': account_id,
                'name': '%s %s' % (account_code, account_name),
                'level': line['level'] + 1,
                'parent_id': line['id'],
                'columns': columns,
                'caret_options': 'account.account',
            })
            line['columns'][column]['name'] += amount
            line['unfolded_lines'][account_id]['columns'][column]['name'] += amount

        def _dispatch_result(account_id, account_code, account_name, account_internal_type, amount, column=0):
            ''' Dispatch the newly fetched line inside the right section. '''
            if account_internal_type == 'receivable':
                # 'Advance Payments received from customers'                (index=3)
                _insert_at_index(3, account_id, account_code, account_name, -amount, column)
            elif account_internal_type == 'payable':
                # 'Advance Payments made to suppliers'                      (index=5)
                _insert_at_index(5, account_id, account_code, account_name, -amount, column)
            elif amount < 0:
                if tag_operating_id in tags_per_account.get(account_id, []):
                    # 'Cash received from operating activities'             (index=4)
                    _insert_at_index(4, account_id, account_code, account_name, -amount, column)
                elif tag_investing_id in tags_per_account.get(account_id, []):
                    # 'Cash in for investing activities'                    (index=8)
                    _insert_at_index(8, account_id, account_code, account_name, -amount, column)
                elif tag_financing_id in tags_per_account.get(account_id, []):
                    # 'Cash in for financing activities'                    (index=11)
                    _insert_at_index(11, account_id, account_code, account_name, -amount, column)
                else:
                    # 'Cash in for unclassified activities'                 (index=14)
                    _insert_at_index(14, account_id, account_code, account_name, -amount, column)
            elif amount > 0:
                if tag_operating_id in tags_per_account.get(account_id, []):
                    # 'Cash paid for operating activities'                  (index=6)
                    _insert_at_index(6, account_id, account_code, account_name, -amount, column)
                elif tag_investing_id in tags_per_account.get(account_id, []):
                    # 'Cash out for investing activities'                   (index=9)
                    _insert_at_index(9, account_id, account_code, account_name, -amount, column)
                elif tag_financing_id in tags_per_account.get(account_id, []):
                    # 'Cash out for financing activities'                   (index=12)
                    _insert_at_index(12, account_id, account_code, account_name, -amount, column)
                else:
                    # 'Cash out for unclassified activities'                (index=15)
                    _insert_at_index(15, account_id, account_code, account_name, -amount, column)

        def _compute_period(option, col_idx=0):
            payment_move_ids, payment_account_ids = self._get_liquidity_move_ids(option)

            # Compute 'Cash and cash equivalents, beginning of period'      (index=0)
            beginning_period_options = self._get_options_beginning_period(option)
            for account_id, account_code, account_name, balance in self._compute_liquidity_balance(beginning_period_options, currency_table_query, payment_account_ids):
                _insert_at_index(0, account_id, account_code, account_name, balance, col_idx)
                _insert_at_index(16, account_id, account_code, account_name, balance, col_idx)

            # Compute 'Cash and cash equivalents, closing balance'          (index=16)
            for account_id, account_code, account_name, balance in self._compute_liquidity_balance(option, currency_table_query, payment_account_ids):
                _insert_at_index(16, account_id, account_code, account_name, balance, col_idx)

            # ==== Process liquidity moves ====
            res = self._get_liquidity_move_report_lines(option, currency_table_query, payment_move_ids, payment_account_ids)
            for account_id, account_code, account_name, account_internal_type, amount in res:
                _dispatch_result(account_id, account_code, account_name, account_internal_type, amount, col_idx)

            # ==== Process reconciled moves ====
            res = self._get_reconciled_move_report_lines(option, currency_table_query, payment_move_ids, payment_account_ids)
            for account_id, account_code, account_name, account_internal_type, balance in res:
                _dispatch_result(account_id, account_code, account_name, account_internal_type, balance, col_idx)

            # 'Cash flows from operating activities'                            (index=2)
            lines_to_compute[2]['columns'][col_idx]['name'] = \
                lines_to_compute[3]['columns'][col_idx]['name'] + \
                lines_to_compute[4]['columns'][col_idx]['name'] + \
                lines_to_compute[5]['columns'][col_idx]['name'] + \
                lines_to_compute[6]['columns'][col_idx]['name']
            # 'Cash flows from investing & extraordinary activities'            (index=7)
            lines_to_compute[7]['columns'][col_idx]['name'] = \
                lines_to_compute[8]['columns'][col_idx]['name'] + \
                lines_to_compute[9]['columns'][col_idx]['name']
            # 'Cash flows from financing activities'                            (index=10)
            lines_to_compute[10]['columns'][col_idx]['name'] = \
                lines_to_compute[11]['columns'][col_idx]['name'] + \
                lines_to_compute[12]['columns'][col_idx]['name']
            # 'Cash flows from unclassified activities'                         (index=13)
            lines_to_compute[13]['columns'][col_idx]['name'] = \
                lines_to_compute[14]['columns'][col_idx]['name'] + \
                lines_to_compute[15]['columns'][col_idx]['name']
            # 'Net increase in cash and cash equivalents'                       (index=1)
            lines_to_compute[1]['columns'][col_idx]['name'] = \
                lines_to_compute[2]['columns'][col_idx]['name'] + \
                lines_to_compute[7]['columns'][col_idx]['name'] + \
                lines_to_compute[10]['columns'][col_idx]['name'] + \
                lines_to_compute[13]['columns'][col_idx]['name']

        self.flush()

        unfold_all = self._context.get('print_mode') or options.get('unfold_all')
        currency_table_query = self._get_query_currency_table(options)
        lines_to_compute = self._get_lines_to_compute(options)

        tag_operating_id = self.env.ref('account.account_tag_operating').id
        tag_investing_id = self.env.ref('account.account_tag_investing').id
        tag_financing_id = self.env.ref('account.account_tag_financing').id
        tag_ids = (tag_operating_id, tag_investing_id, tag_financing_id)
        tags_per_account = self._get_tags_per_account(options, tag_ids)

        _compute_period(options)
        if options.get('comparison') and options['comparison'].get('periods'):
            for idx, period in enumerate(options['comparison']['periods']):
                option = options.copy()
                option['date'] = period
                _compute_period(option, idx+1)

        # ==== Compute the unexplained difference ====
        delta_columns = []
        for idx in range(len(lines_to_compute[0]['columns'])):
            closing_ending_gap = lines_to_compute[16]['columns'][idx]['name'] - lines_to_compute[0]['columns'][idx]['name']
            computed_gap = sum(lines_to_compute[index]['columns'][idx]['name'] for index in [2, 7, 10, 13])
            delta = closing_ending_gap - computed_gap
            if self.env.company.currency_id.is_zero(delta):
                delta = False
            delta_columns.append(delta)

        if any(delta_columns):
            columns = []
            for delta in delta_columns:
                if delta:
                    columns.append({'name': delta, 'class': 'number'})
                else:
                    columns.append({'name': 0.0, 'class': 'number'})

            lines_to_compute.insert(16, {
                'id': 'cash_flow_line_unexplained_difference',
                'name': _('Unexplained Difference'),
                'level': 0,
                'columns': columns,
            })

        # ==== Build final lines ====

        lines = []
        for line in lines_to_compute:
            unfolded_lines = line.pop('unfolded_lines', {})
            sub_lines = [unfolded_lines[k] for k in sorted(unfolded_lines)]

            line['unfoldable'] = len(sub_lines) > 0
            line['unfolded'] = line['unfoldable'] and (unfold_all or line['id'] in options['unfolded_lines'])

            # Header line.
            for column in line['columns']:
                column['name'] = self.format_value(column['name'])
            lines.append(line)

            # Sub lines.
            for sub_line in sub_lines:
                for column in sub_line['columns']:
                    column['name'] = self.format_value(column['name'])
                sub_line['style'] = '' if line['unfolded'] else 'display: none;'
                lines.append(sub_line)

            # Total line.
            if line['unfoldable']:
                lines.append({
                    'id': '%s_total' % line['id'],
                    'name': _('Total') + ' ' + line['name'],
                    'level': line['level'] + 1,
                    'parent_id': line['id'],
                    'columns': line['columns'],
                    'class': 'o_account_reports_domain_total',
                    'style': '' if line['unfolded'] else 'display: none;',
                })
        return lines
