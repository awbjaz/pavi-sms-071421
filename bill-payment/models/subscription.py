from odoo import models

import logging

_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    def _prepare_invoice_statement(self, invoice):
        self.ensure_one()
        device_id = self.env.ref('awb_subscriber_product_information.product_device_fee').id
        lines = []
        # invoice Lines
        for invoice_line in invoice['invoice_line_ids']:
            line = invoice_line[2]
            _logger.debug(f'Line: {line}')
            product = self.env['product.product'].browse(line['product_id'])
            _logger.debug(f'Prod ID temp {product.product_tmpl_id.id}')

            total_vat = 0.0
            for taxes in line['tax_ids']:
                vat = taxes[2]
                args = [('id', 'in', vat)]
                tax = self.env['account.tax'].search(args)
                total_price_unit = line['price_unit'] * \
                    line['quantity']  # 1999
                tot_vat = 0.0
                for t in tax:
                    total_price_unit = total_price_unit - tot_vat
                    # tax exclusive
                    # total_vat += total_price_unit * tax.amount / 100
                    # tax inclusive
                    tot_vat += (total_price_unit /
                                ((100 + t.amount) / 100)) * (t.amount/100)
                total_vat += tot_vat

            if product.product_tmpl_id.id == device_id:
                data = {
                    'name': line['name'],
                    'statement_type': 'device_fee',
                    'amount': line['price_unit'] - total_vat,
                }
                lines.append((0, 0, data))
            else:
                data = {
                    'name': line['name'],
                    'statement_type': 'subs_fee',
                    'amount': (line['price_unit'] * line['quantity']) - total_vat,
                }
                lines.append((0, 0, data))

            data = {'name': "Value Added Tax", 'statement_type': 'vat'}
            data['amount'] = total_vat
            lines.append((0, 0, data))

        # invoice previous bill
        args = [('partner_id', '=', invoice['partner_id']),
                ('type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('is_subscription', '=', True),
                ('invoice_date_due', '<', invoice['invoice_date_due']),
                ('invoice_line_ids.subscription_id', '=', self.id)]

        invoice_id = self.env['account.move'].search(args, limit=1, order="invoice_date_due desc")
        _logger.debug(f'Prev_bIll {invoice_id}')
        if invoice_id:
            prev_bill = invoice_id.amount_total + invoice_id.total_prev_charges
            prev_bill = {
                'name': 'Previous Bill balance',
                'statement_type': 'prev_bill',
                'amount': prev_bill,
            }
            lines.append((0, 0, prev_bill))

            total_payment = 0.0
            for payment in invoice_id.payment_ids:
                total_payment += payment.amount

            prev_payment = {
                'name': 'Previous Received Payment',
                'statement_type': 'payment',
                'amount': total_payment * -1,
            }
            lines.append((0, 0, prev_payment))

        #Rebates
        args_rebates = [('partner_id', '=', invoice['partner_id']),
                ('type', '=', 'out_refund'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', invoice['start_date']),
                ('invoice_date', '<=', invoice['end_date'])]

        credit_note_id = self.env['account.move'].search(args_rebates, order="invoice_date desc")
        
        if credit_note_id:
            total_rebates = 0.0
            for rebates in credit_note_id:
                total_rebates += rebates.amount_total

            rebates = {
                'name': 'Rebates',
                'statement_type': 'adjust',
                'amount': total_rebates * -1,
            }
            lines.append((0, 0, rebates))

        return lines
