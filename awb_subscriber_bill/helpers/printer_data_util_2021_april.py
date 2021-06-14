# -*- coding: utf-8 -*-
from .printer_data_util import PrinterDataUtil
import logging

_logger = logging.getLogger(__name__)


# https://pavi-test-staging-new-2381758.dev.odoo.com/print/custom/sales_invoice/690595

class PrinterDataUtil(PrinterDataUtil):

    @classmethod
    def _format_number(cls, value):
        result = '0.00'
        if value:
            result = '{0:.2f}'.format(value)
        return result

    @classmethod
    def _format_date_mmddyyyy(cls, value):
        return cls._format_date(value)

    @classmethod
    def _format_string(cls, value):
        result = ''
        _logger.error(value)
        if value:
            result = value + ''
        return result

    @classmethod
    def _generate_data_row(cls, record):
        delim = '|'
        fields = []

        # Subscriber Name
        fields.append(record.partner_id.name)

        # Address fields
        fields.append(cls._format_string(record.company_id.street) + ',' + cls._format_string(record.company_id.street2))
        fields.append(cls._format_string(record.company_id.city) + ',' + cls._format_string(record.company_id.state_id.name))

        # Account Number
        account_number = record.partner_id.customer_number
        fields.append(account_number)
        # ATM Reference Number
        atm_ref = record.print_atm_ref(record.atm_ref)
        fields.append(atm_ref)

        # Bill Number
        fields.append(record.name)
        # Bill Period
        fields.append(cls._format_date_mmddyyyy(record.start_date) + ' - ' + cls._format_date_mmddyyyy(record.end_date))

        # Min Due
        # fields.append(record.amount_total_signed)
        fields.append(cls._format_number(record.total_statement_balance))
        # Total Amount
        fields.append(cls._format_number(record.total_statement_balance))
        # Due Date
        fields.append(cls._format_date_mmddyyyy(record.invoice_date_due))
        # Plan
        val = ''
        try: 
            val = record.invoice_line_ids[0].product_id.name
        except:
            pass
        fields.append(val)

        # Previous Bill balance 
        val = 0.0
        for line in record.statement_line_ids:
            if line.statement_type == 'prev_bill':
                val = val + line.amount
        fields.append(cls._format_number(val))
        # Previous received
        val = 0.0
        for line in record.statement_line_ids:
            if line.statement_type == 'payment':
                val = val + line.amount
        fields.append(cls._format_number(val))
        # Add adjustment
        val = 0.0
        for line in record.statement_line_ids:
            if line.statement_type == 'adjust':
                val = val + line.amount
        fields.append(cls._format_number(val))
        # Total Previous Charges
        fields.append(cls._format_number(record.total_prev_charges))

        # Monthly Subscription Fee
        val = 0.0
        for line in record.statement_line_ids:
            if line.statement_type == 'subs_fee':
                val = val + line.amount
        fields.append(cls._format_number(val))
        # Device Fee
        val = 0.0
        for line in record.statement_line_ids:
            if line.statement_type == 'device_fee':
                val = val + line.amount
        fields.append(cls._format_number(val))
        # Others
        val = 0.0
        for line in record.statement_line_ids:
            if line.statement_type == 'other':
                val = val + line.amount
        fields.append(cls._format_number(val))
        # VAT
        fields.append(cls._format_number(record.total_vat))

        # Total Current Charges
        fields.append(cls._format_number(record.amount_total))
        # TOTAL AMOUNT DUE
        fields.append(cls._format_number(record.total_statement_balance))

        # Reminders
        val = '''Thank you very much for settling your Streamtech monthly bill on time. We acknowledge your timely update, and would like you to know that this helps us at Streamtech to constantly provide you with quality internet service for your home. Please be reminded that any payments made on or after''' + cls._format_date_mmddyyyy(record.posting_date) + ''' will be reflected on your next billing statement. Should there be any billing discrepancies in your statement of account, kindly coordinate with our Billing Department within 15 days from statement date, or this statement of account would be considered accurate.'''
        fields.append(val)

        # Account Number
        fields.append(account_number)
        # Name
        val = ''
        if record.partner_id.company_type == 'person':
            val = record.partner_id.first_name
            if record.partner_id.middle_name:
                val += ' ' + record.partner_id.middle_name[:1] + '.'
            val += ' ' + record.partner_id.last_name
        elif record.partner_id.is_company:
            val = record.partner_id.name
        fields.append(val)
        # Due Date
        fields.append(record.invoice_date_due)
        # Total Amount Due
        fields.append(cls._format_number(record.total_statement_balance))
        # ATM Reference Number
        fields.append(atm_ref)

        # # Contact Number (not included by PAVI in their mapping)
        # fields.append(record.partner_id.phone)

        # Barcode Contents: ATM Reference Number
        fields.append(atm_ref)
        # QRCode
        fields.append('')
        # Extra
        fields.append('')

        # ATM Reference Number
        fields.append(atm_ref)
        # Due Date
        fields.append(record.invoice_date_due)
        # Customer Name
        fields.append(record.partner_id.name)

        # Received by
        fields.append(record.partner_id.name)

        # for f in fields:
        #     _logger.error('> ' + str(f))
        #     if isinstance(f, float):
        #         _logger.error('FLOAT')

        # txt = delim.join(fields)
        txt = delim.join(map(str, fields))
        return txt

