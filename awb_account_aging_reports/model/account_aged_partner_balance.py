from odoo import api, models, _
from odoo.tools.misc import format_date
import logging


_logger = logging.getLogger(__name__)


class report_account_aged_partner(models.AbstractModel):
    _inherit = "account.aged.partner"

    filter_analytic = True

    def _get_options(self, previous_options=None):
        _logger.debug(f'Prev Options: {previous_options}')
        options = super(report_account_aged_partner, self)._get_options(previous_options)
        if 'account_accounts' not in previous_options.keys():
            options['account_accounts'] = []

        if options.get('account_accounts') is not None:
            options['selected_account_accounts_names'] = [self.env['account.account'].browse(int(account)).name for account in options['account_accounts']]
        return options

    @api.model
    def _init_filter_analytic(self, options, previous_options=None):
        super()._init_filter_analytic(options, previous_options)
        options['account_accounts'] = previous_options and previous_options.get('account_accounts') or []
        account_account_ids = [int(tag) for tag in options['account_accounts']]
        selected_account_accounts = account_account_ids \
                                    and self.env['account.account'].browse(account_account_ids) \
                                    or self.env['account.account']
        options['selected_account_account_names'] = selected_account_accounts.mapped('name')

    @api.model
    def _get_lines(self, options, line_id=None):
        _logger.debug(f'Options: {options}')

        sign = -1.0 if self.env.context.get('aged_balance') else 1.0
        lines = []
        account_types = [self.env.context.get('account_type')]
        context = {'include_nullified_amount': True}
        if line_id and 'partner_' in line_id:
            # we only want to fetch data about this partner because we are expanding a line
            partner_id_str = line_id.split('_')[1]
            if partner_id_str.isnumeric():
                partner_id = self.env['res.partner'].browse(int(partner_id_str))
            else:
                partner_id = False
            context.update(partner_ids=partner_id)

        analytic_accounts = options.get('analytic_accounts', [])
        analytic_tags = options.get('analytic_tags', [])
        accounts = options.get('account_accounts', [])

        if len(analytic_accounts) or len(analytic_tags) or len(accounts):
            if len(analytic_accounts):
                context.update(analytic_accounts=analytic_accounts)

            if len(analytic_tags):
                context.update(analytic_tags=analytic_tags)

            if len(accounts):
                context.update(account_accounts=accounts)

            results, total, amls = self.env['report.account.report_agedpartnerbalance_account'].with_context(**context)._get_partner_move_lines(account_types, self._context['date_to'], 'posted', 30)
        else:
            results, total, amls = self.env['report.account.report_agedpartnerbalance'].with_context(**context)._get_partner_move_lines(account_types, self._context['date_to'], 'posted', 30)

        for values in results:
            vals = {
                'id': 'partner_%s' % (values['partner_id'],),
                'name': values['name'],
                'level': 2,
                'columns': [{'name': ''}] * 4 + [{'name': self.format_value(sign * v), 'no_format': sign * v}
                                                 for v in [values['direction'], values['4'],
                                                           values['3'], values['2'],
                                                           values['1'], values['0'], values['total']]],
                'trust': values['trust'],
                'unfoldable': True,
                'unfolded': 'partner_%s' % (values['partner_id'],) in options.get('unfolded_lines'),
                'partner_id': values['partner_id'],
            }
            lines.append(vals)
            if 'partner_%s' % (values['partner_id'],) in options.get('unfolded_lines'):
                for line in amls[values['partner_id']]:
                    aml = line['line']
                    if aml.move_id.is_purchase_document():
                        caret_type = 'account.invoice.in'
                    elif aml.move_id.is_sale_document():
                        caret_type = 'account.invoice.out'
                    elif aml.payment_id:
                        caret_type = 'account.payment'
                    else:
                        caret_type = 'account.move'

                    line_date = aml.date_maturity or aml.date
                    if not self._context.get('no_format'):
                        line_date = format_date(self.env, line_date)
                    vals = {
                        'id': aml.id,
                        'name': aml.move_id.name,
                        'class': 'date',
                        'caret_options': caret_type,
                        'level': 4,
                        'parent_id': 'partner_%s' % (values['partner_id'],),
                        'columns': [{'name': v} for v in [format_date(self.env, aml.date_maturity or aml.date), aml.journal_id.code, aml.account_id.display_name, format_date(self.env, aml.expected_pay_date)]] +
                                   [{'name': self.format_value(sign * v, blank_if_zero=True), 'no_format': sign * v} for v in [line['period'] == 6-i and line['amount'] or 0 for i in range(7)]],
                        'action_context': {
                            'default_type': aml.move_id.type,
                            'default_journal_id': aml.move_id.journal_id.id,
                        },
                        'title_hover': self._format_aml_name(aml.name, aml.ref, aml.move_id.name),
                    }
                    lines.append(vals)
        if total and not line_id:
            total_line = {
                'id': 0,
                'name': _('Total'),
                'class': 'total',
                'level': 2,
                'columns': [{'name': ''}] * 4 + [{'name': self.format_value(sign * v), 'no_format': sign * v} for v in [total[6], total[4], total[3], total[2], total[1], total[0], total[5]]],
            }
            lines.append(total_line)
        return lines
