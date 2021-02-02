from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"
    _description = "Subscription"

    remaining_months = fields.Float(string="Remaining Months", compute='compute_remaining_months')
    paid_security_deposit = fields.Float(string="Paid Security Deposit")
    rebates = fields.Float(string="Rebates")
    promo = fields.Float(string="Promo")
    baseline_amount = fields.Float(string="Baseline Amount")
    discount = fields.Float(string="Discount Amount")
    termination_item = fields.Many2one('product.product', string="Termination Item")
    pre_termination_charge = fields.Float(string="Pre-Termination Charge", compute='compute_pre_termination_charge')

    def compute_remaining_months(self):
        for rec in self:
            if rec.subscription_status == 'pre-termination':
                invoice_args = [
                                ('invoice_line_ids.subscription_id', '=', rec.id),
                                ('state', 'in', ['draft','posted'])]
                invoices = self.env['account.move'].search(invoice_args)
                invoice_count = len(invoices)
                template = rec.template_id
                recurring_rule_boundary = template.recurring_rule_boundary
                if recurring_rule_boundary == 'limited':
                    total_duration = template.recurring_rule_count
                else:
                    total_duration = 0
                rec.remaining_months = abs(invoice_count - total_duration)
            else:
                rec.remaining_months = 0

    def compute_pre_termination_charge(self):
        pre_termination_charge = 0
        for rec in self:
            if rec.subscription_status == 'pre-termination':
                remaining_months = rec.remaining_months
                recurring_total = rec.recurring_total
                paid_security_deposit = rec.paid_security_deposit
                rebates = rec.rebates
                promo = rec.promo
                discount = rec.discount
                baseline_amount = rec.baseline_amount

                pre_termination_charge = (
                    (remaining_months *
                        recurring_total) -
                    (paid_security_deposit +
                        rebates +
                        promo +
                        discount))

                if baseline_amount > pre_termination_charge:
                    rec.pre_termination_charge = baseline_amount
                else:
                    rec.pre_termination_charge = pre_termination_charge
            else:
                rec.pre_termination_charge = 0

    def recurring_invoice(self):
        if self.subscription_status == 'pre-termination':
            invoice_data = []
            for record in self:
                invoice_raw_data = {
                            'product_id': record.termination_item.id,
                            'price_unit': record.pre_termination_charge,
                            "quantity": 1,
                            "subscription_id": self.id
                            }
                invoice_data.append((0, 0, invoice_raw_data))

            self.env['account.move'].sudo().create({
                'partner_id': self.partner_id.id,
                'invoice_date': date.today(),
                'invoice_origin': self.code,
                'invoice_line_ids': invoice_data,
                'type': 'out_invoice',
                })
            return self.action_subscription_invoice()
        else:
            return super(SaleSubscription, self).recurring_invoice()