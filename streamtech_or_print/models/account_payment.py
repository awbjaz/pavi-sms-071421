from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class account_payment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def amount_to_text(self, amount, currency):
        convert_amount_in_words = currency.amount_to_text(amount)
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' Only ')
        return convert_amount_in_words

    @api.model
    def get_details(self):
        detail = {
            'device_fee': 0.0,
            'service_fee': 0.0,
            'untaxed_amount': 0.0,
            'total_sales': 0.0,
            'vat': 0.0,
            'total_amount': 0.0
        }
        device = self.env.ref('awb_subscriber_product_information.product_device_fee')
        for invoice in self.reconciled_invoice_ids:
            detail['untaxed_amount'] += invoice.amount_untaxed
            detail['vat'] += invoice.amount_tax
            detail['total_sales'] += invoice.amount_total
            detail['total_amount'] += invoice.amount_total
            for line in invoice.invoice_line_ids:
                if line.product_id.id == device.id:
                    detail['device_fee'] += line.price_subtotal
                else:
                    detail['service_fee'] += line.price_subtotal
                _logger.info(f'Invoice {invoice} {line} {detail}')
        return detail
