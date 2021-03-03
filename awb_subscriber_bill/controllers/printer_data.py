# -*- coding: utf-8 -*-
import logging
from io import BytesIO
from tempfile import TemporaryFile

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class PrinterDataController(http.Controller):

    @classmethod
    def _format_number(cls, value, length):
        result = '0.00'
        if value:
            result = '{0:.2f}'.format(value)
        return result.rjust(length)

    @classmethod
    def _format_string(cls, value, length):
        result = ''
        if value:
            result = value + ''
        return result.ljust(length)

    @classmethod
    def _format_date(cls, value):
        date = str(value)
        if(date.endswith('False')):
            date = date[:-len('False')]
        else:
            date += ''
        return date
    
    @classmethod
    def _format_date_mmyyyy(cls, value):
        value = cls._format_date(value)
        if value and len(value) > 0:
            value = value[0:2] + '-' + value[6:10]
        return value.ljust(10)

    @classmethod
    def _format_date_mmddyyyy(cls, value):
        return cls._format_date(value).ljust(10)

    @classmethod
    def _format_date_range(cls, value1, value2):
        return cls._format_date(value1) + ' to ' + cls._format_date(value2)

    @http.route(['/print/custom/sales_invoice/<int:account_invoice_id>'], type='http', auth='user', methods=['GET'])
    def report_voucher(self, account_invoice_id, data=None, **args):
        _logger.debug('HELLO')
        record = request.env['account.move'].browse(account_invoice_id)

        txt = ''
        txt += PrinterDataController._format_string(record.name, 10)
        txt += PrinterDataController._format_date_mmyyyy(record.invoice_date)
        txt += PrinterDataController._format_date_mmddyyyy(record.invoice_date_due)
        txt += PrinterDataController._format_date_mmddyyyy('')

        txt += PrinterDataController._format_string(record.invoice_line_ids[0].subscription_id.account_identification, 20)
        txt += PrinterDataController._format_string(record.invoice_partner_display_name, 70)

        value = ''
        try:
            value = record.partner_id.street + ', ' + record.partner_id.street2
        except:
            pass 
        txt += PrinterDataController._format_string(value, 64)
        txt += PrinterDataController._format_string(record.partner_id.city, 64)

        value = ''
        try:
            value = record.invoice_line_ids[0].name
        except:
            pass 
        txt += PrinterDataController._format_string(value, 12)

        txt += PrinterDataController._format_string('0', 10)
        txt += PrinterDataController._format_string('0', 10)
        txt += PrinterDataController._format_string('0', 10)

        txt += PrinterDataController._format_string('', 20)
        txt += PrinterDataController._format_string(record.period_covered, 24)

        txt += PrinterDataController._format_string('Balance from Last Bill', 50)
        txt += PrinterDataController._format_string('Basic Charge', 30)
        txt += PrinterDataController._format_string('Reconnection Fee', 30)
        txt += PrinterDataController._format_string('Other Charges', 30)
        txt += PrinterDataController._format_string('', 30)
        txt += PrinterDataController._format_string('', 30)
        txt += PrinterDataController._format_string('<Reserved Blank1>', 30)
        txt += PrinterDataController._format_string('<Reserved Blank2>', 30)
        txt += PrinterDataController._format_string('Total Charges', 30)
        txt += PrinterDataController._format_string('12% VAT', 30)
        txt += PrinterDataController._format_string('Amortization of Promissory Note', 40)
        txt += PrinterDataController._format_string('Minimum Amount Due (Php)', 30)
        txt += PrinterDataController._format_string('Remarks:', 8)

        txt += PrinterDataController._format_number(record.total_prev_charges, 12)
        txt += PrinterDataController._format_number(record.invoice_line_ids[0].subscription_id.baseline_amount, 12)

        txt += PrinterDataController._format_string('(Inclusive of VAT)', 19)
        txt += PrinterDataController._format_number(0, 12)
        txt += PrinterDataController._format_number(record.invoice_line_ids[0].subscription_id.paid_security_deposit, 12)
        txt += PrinterDataController._format_number(0, 12)
        txt += PrinterDataController._format_number(record.amount_total, 12)
        txt += PrinterDataController._format_number(record.total_vat, 12)
        txt += PrinterDataController._format_number(0, 12) # amort
        txt += PrinterDataController._format_number(record.amount_total_signed, 12)

        txt += PrinterDataController._format_string('', 120)
        txt += PrinterDataController._format_string('', 120)

        txt += PrinterDataController._format_string(record.atm_ref, 100)

        headers = [
                ('Content-Type', 'text/html'), 
                ('Content-Length', len(txt)), 
                ('Content-Disposition', 'attachment; filename="printer_data.txt"')
            ]
        return request.make_response(txt, headers=headers)

    @classmethod
    def generate_data_row(cls, data):
        return ''

