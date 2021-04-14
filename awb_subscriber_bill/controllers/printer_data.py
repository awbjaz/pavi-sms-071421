# -*- coding: utf-8 -*-
import logging
from io import BytesIO
from tempfile import TemporaryFile
from odoo import http
from odoo.http import request

from ..helpers.printer_data_util import PrinterDataUtil

_logger = logging.getLogger(__name__)

class PrinterDataController(http.Controller):

    @http.route(['/print/custom/sales_invoice/<string:account_invoice_ids>'], type='http', auth='user', methods=['GET'])
    def report_voucher(self, account_invoice_ids, data=None, **args):
        _logger.error(f'/print/custom/sales_invoice/<string:account_invoice_ids {account_invoice_ids}')
        account_ids = account_invoice_ids.split("-")
        records = request.env['account.move'].search([('id', 'in', account_ids)])
        txt = PrinterDataUtil.generate_data_file_contents(records)

        headers = [
                ('Content-Type', 'text/html'), 
                ('Content-Length', len(txt)), 
                ('Content-Disposition', 'attachment; filename="printer_data.txt"')
            ]
        return request.make_response(txt, headers=headers)



    @classmethod
    def generate_data_row(cls, data):
        return ''

