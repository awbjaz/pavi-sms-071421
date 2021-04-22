# -*- coding: utf-8 -*-

import logging

from odoo import fields, models, api, _
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)

TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale_refund',
    'in_refund': 'purchase_refund',
}


class AccountMoveBatch(models.Model):
    _name = "account.move.batch"
    _description = "Account Batch Rebates"

    @api.model
    def _get_company_default(self):
        company_env = self.env['res.company']
        default_company_id = company_env._company_default_get('account.move.batch')
        return company_env.browse(default_company_id.id)

    @api.model
    def _default_journal(self):
        if self._context.get('default_journal_id', False):
            return self.env['account.move'].browse(self._context.get('default_journal_id'))
        inv_type = self._context.get('type', 'out_invoice')
        inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        domain = [
            ('type', 'in', [TYPE2JOURNAL[ty] for ty in inv_types if ty in TYPE2JOURNAL]),
            ('company_id', '=', company_id),
        ]
        return self.env['account.move'].search(domain, limit=1)

    name = fields.Char(string='Sequence', readonly=True, default="MASS INV/", required=True)
    invoice_type = fields.Selection([('cust_invoice', 'Customer Invoice')],
                                    string="Invoice Type", default='cust_invoice')
    company_id = fields.Many2one('res.company', string='Company', default=_get_company_default)
    rebate_date = fields.Date(string="Date", required=True, default=fields.Date.today())
    journal_id = fields.Many2one('account.move', string='Journal', default=_default_journal)
    location_id = fields.Many2one('subscriber.location', string='Location')
    days = fields.Integer(string="Number of Days")

    invoice_ids = fields.One2many('account.move.batch.line', 'invoice_id', string="Invoice")
    account_move_ids = fields.One2many('account.move', 'batch_rebates_id', string='Invoices')

    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('invoice', 'Invoiced'),
                              ('post', 'Posted')],
                             string='State', default='draft')
    account_invoice_ids = fields.Many2many('account.move', string="Invoices")
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'account.move.batch.seq.code') or 'MASS INV/'
        result = super(AccountMoveBatch, self).create(vals)
        return result

    def action_set_to_draft(self):
        self.write({'state':'draft'})

    def action_compute_rebates(self):
        _logger.debug(f'Computing Rebates')
        if self.invoice_ids:
            for line in self.invoice_ids:
                rebates = self.days / 30 * line.subscription_line_id.price_subtotal
                line.update({'amount': rebates})
                _logger.debug(f'Subs Line {line}')
                
    def action_load_subscribers(self):
        _logger.debug(f'Loading Subscribers')
        if not self.location_id:
            raise UserError(_('Please select a location first. Before loading subscribers.'))

        stages = self.env['sale.subscription.stage'].search([('in_progress', '=', True)]).mapped('id')
        _logger.debug(f'Stages {stages}')
        subs = self.location_id.subscription_ids.filtered(lambda s: s.stage_id.id in stages)

        _logger.debug(f'Subscriptions: {subs}')
        subscription_ids = []
        sub_product = []
        for sub in subs:
            partner = sub.partner_id
            # date = sub.date_start
            device_id = self.env.ref('awb_subscriber_product_information.product_device_fee').id
            for sub_line in sub.recurring_invoice_line_ids:
                if sub_line.product_id.id != device_id:
                    data = {
                        'date': self.rebate_date,
                        'subscription_line_id': sub_line.id,
                        'partner_id': partner.id,
                        'product_id': sub_line.product_id.id,
                        'description': sub_line.name,
                        'uom_id': sub_line.uom_id.id,
                        'amount': 0
                    }

                    sub_product.append((0, 0, data))
        self.update({'invoice_ids': None})
        self.update({'invoice_ids': sub_product})
        
        return True

    def action_confirm(self):
        self.write({'state': 'confirm'})
        return True

    def action_invoice(self):
        _logger.debug(f'Create Invoice')

        customers = {}
        for line in self.invoice_ids:
            customer_id = line.partner_id.id

            if customer_id not in customers:
                customers[customer_id] = {
                    'customer_id': customer_id,
                    'lines': []
                }
            customers[customer_id]['lines'].append(line)

        _logger.debug(f'Customers {customers}')

        for customer_id, batch_lines in customers.items():
            invoice_lines = []
            for line in batch_lines['lines']:
                account_id = line.product_id.categ_id.property_account_income_categ_id
                invoice_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.description,
                    'account_id': account_id.id,
                    'price_unit': line.amount,
                    'quantity': 1,
                }))

            data = {
                'invoice_origin': self.name,
                'invoice_date': line.date,
                'date': fields.Date.today(),
                'partner_id': customer_id,
                'type': 'out_refund',
                'invoice_line_ids': invoice_lines,
                'batch_rebates_id': self._origin.id,
            }

            credit_notes_id = self.env['account.move'].create(data)
            _logger.debug(f'Credit Notes {credit_notes_id}')
            self.update({'state': 'invoice'})
      

    def action_view_invoice(self):
        view_id = []
        for moves in self.account_move_ids:
            view_id.append(moves.id)
        form_view = self.env.ref('account.view_move_form', False)
        action = self.env.ref('account.action_move_out_refund_type').read()[0]
        action['views'] = [(self.env.ref('account.view_invoice_tree').id, 'tree'),
                           (form_view.id, 'form')]
        action['domain'] = "[('id', 'in', " + str(view_id) + ")]"
        return action

    def action_invoice_post(self):
        view_id = []
        for moves in self.account_move_ids:
            view_id.append(moves.id)
        move = self.env['account.move'].search([('id', 'in', view_id)])
        move.action_post()
        self.update({'state': 'post'})


class AccountMoveBatchLine(models.Model):
    _name = "account.move.batch.line"
    _description = "Account Batch Rebates Line"

    invoice_id = fields.Many2one('account.move.batch', string="Invoice")
    partner_id = fields.Many2one('res.partner', string="Partner", required=True)
    description = fields.Char(string="Description")
    date = fields.Date(string="Date", default=fields.Date.today(), required=True)
    uom_id = fields.Many2one('uom.uom', string="UOM")
    product_id = fields.Many2one('product.product', string='Product')
    account_id = fields.Many2one('account.account', string="Account")
    amount = fields.Float(string="Amount", required=True)
    subscription_line_id = fields.Many2one('sale.subscription.line', string="Subscription Line")
