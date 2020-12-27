from odoo import models, api


class account_payment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = currency.amount_to_text(amount)
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' Only ')
        return convert_amount_in_words
