from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class account_payment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = currency.amount_to_text(amount)
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' Only ')
        convert_amount_in_words = convert_amount_in_words.replace(',','').replace('Peso', 'Pesos Only').replace('\n', '')
        return convert_amount_in_words

    def __get_address_field(self, field, is_comma_needed):
        address = ''
        if field and len(field) > 0:
            address +=  field
            if is_comma_needed:
                address += ', '
        return address

    @api.model
    def get_full_address_text(self):
        address = '' 
        address += self.__get_address_field(self.partner_id.street, True) 
        address += self.__get_address_field(self.partner_id.street2, True) 
        address += self.__get_address_field(self.partner_id.city, True) 
        address += self.__get_address_field(self.partner_id.state_id.name, False)
        return address

    @api.model
    def get_details(self):
        detail = {
            'device_fee': 0.0,
            'service_fee': 0.0,
            'untaxed_amount': 0.0,
            'tax_withholding': 0.0,
            'total_sales': 0.0,
            'vat': 0.0,
            'total_amount': 0.0
        }
        detail['total_sales'] = float(self.amount)
        detail['vat'] = round(self.amount / 1.12 * 0.12, 2)
        detail['untaxed_amount'] = round(detail['total_sales'] - detail['vat'], 2)
        if self.partner_id.is_company:
            detail['tax_withholding'] = round(detail['untaxed_amount'] * 0.02, 2)
        detail['total_amount'] = round(detail['untaxed_amount'] + detail['vat'] - detail['tax_withholding'], 2)

        return detail
