# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import UserError
from odoo.tools.misc import format_date
from odoo.addons.account.models.account_move import AccountMove as OriginalAccountMove


def _check_fiscalyear_lock_date(self):
    for move in self.filtered(lambda move: move.state == 'posted'):
        lock_date = max(move.company_id.period_lock_date or date.min, move.company_id.fiscalyear_lock_date or date.min)
        if self.user_has_groups('account.group_account_manager') or self.user_has_groups('account.group_account_user'):
            lock_date = move.company_id.fiscalyear_lock_date
        if move.date <= (lock_date or date.min):
            if self.user_has_groups('account.group_account_manager') or self.user_has_groups('account.group_account_user'):
                message = _("You cannot add/modify entries prior to and inclusive of the lock date %s.") % format_date(self.env, lock_date)
            else:
                message = _("You cannot add/modify entries prior to and inclusive of the lock date %s. Check the company settings or ask someone with the 'Adviser and Accountant' role") % format_date(self.env, lock_date)
            raise UserError(message)
    return True


OriginalAccountMove._check_fiscalyear_lock_date = _check_fiscalyear_lock_date