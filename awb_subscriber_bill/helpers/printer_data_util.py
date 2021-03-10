# -*- coding: utf-8 -*-
import logging
import datetime

_logger = logging.getLogger(__name__)

class PrinterDataUtil():

    @classmethod
    def _format_number(cls, value, length):
        result = '0.00'
        try:
            result = '{0:.2f}'.format(value)
        except:
            pass
        return result.rjust(length)

    @classmethod
    def _format_string(cls, value, length):
        result = ''
        if value:
            result = value + ''
        return result.ljust(length)

    @classmethod
    def _format_date(cls, value):
        date = ''
        try:
            date = datetime.date.strftime(value, "%m-%d-%Y")
        except:
            pass

        return date
    
    @classmethod
    def _format_date_mmyyyy(cls, value):
        value = cls._format_date(value)
        if value and len(value) > 0:
            value = value[0:2].rjust(2,'0') + '-' + value[6:10].rjust(2,'0')
        return value.ljust(10)

    @classmethod
    def _format_date_mmddyyyy(cls, value):
        return cls._format_date(value).ljust(10)

    @classmethod
    def _format_date_range(cls, value1, value2):
        return cls._format_date(value1) + ' to ' + cls._format_date(value2)

    @classmethod
    def _generate_data_row(cls, record):
        txt = ''
        txt += cls._format_string(record.name.replace('INV/',''), 10)
        txt += cls._format_date_mmyyyy(record.invoice_date)
        txt += cls._format_date_mmddyyyy(record.invoice_date_due)
        txt += cls._format_date_mmddyyyy('')

        txt += cls._format_string(record.partner_id.customer_number, 20)
        txt += cls._format_string(record.invoice_partner_display_name, 70)

        value = ''
        try:
            value = record.partner_id.street + ', ' + record.partner_id.street2
        except:
            pass 
        txt += cls._format_string(value, 64)
        txt += cls._format_string(record.partner_id.city_id.name, 64)

        value = ''
        try:
            value = record.invoice_line_ids[0].name
        except:
            pass 
        txt += cls._format_string(value, 12)

        txt += cls._format_string('0', 10)
        txt += cls._format_string('0', 10)
        txt += cls._format_string('0', 10)

        txt += cls._format_string('', 20)
        txt += cls._format_string(record.period_covered, 24)
        txt += cls._format_date_range(record.start_date, record.end_date)

        txt += cls._format_string('Balance from Last Bill', 50)
        txt += cls._format_string('Basic Charge', 30)
        txt += cls._format_string('Reconnection Fee', 30)
        txt += cls._format_string('Other Charges', 30)
        txt += cls._format_string('', 30)
        txt += cls._format_string('', 30)
        txt += cls._format_string('<Reserved Blank1>', 30)
        txt += cls._format_string('<Reserved Blank2>', 30)
        txt += cls._format_string('Total Charges', 30)
        txt += cls._format_string('12% VAT', 30)
        txt += cls._format_string('Amortization of Promissory Note', 40)
        txt += cls._format_string('Minimum Amount Due (Php)', 30)
        txt += cls._format_string('Remarks:', 8)

        txt += cls._format_number(record.total_prev_charges, 12)

        subs_tot = 0
        for line in record.statement_line_ids:
            if line.statement_type == 'subs_fee':
                subs_tot = subs_tot + line.amount
        txt += cls._format_number(subs_tot, 12)

        txt += cls._format_string('(Inclusive of VAT)', 19)
        txt += cls._format_number(0, 12)
        txt += cls._format_number(record.invoice_line_ids[0].subscription_id.paid_security_deposit, 12)
        txt += cls._format_number(0, 12)
        txt += cls._format_number(record.amount_total, 12)
        txt += cls._format_number(record.total_vat, 12)
        txt += cls._format_number(0, 12) # amort
        txt += cls._format_number(record.amount_total_signed, 12)

        txt += cls._format_string('', 120)
        txt += cls._format_string('', 120)

        txt += cls._format_string(record.atm_ref, 100)

        return txt

    @classmethod
    def generate_data_file_contents(cls, records):

        txt = ''
        for record in records:
            txt += cls._generate_data_row(record) + "\n"

        _logger.error(f'generate_data_file {txt}')
        return txt
