# -*- coding: utf-8 -*-

from odoo import fields, models

import logging

_logger = logging.getLogger(__name__)


class CRMStage(models.Model):
    _inherit = "crm.stage"

    is_auto_quotation = fields.Boolean(string='Automatic Quotation')


class CRMProductLine(models.Model):
    _name = 'crm.lead.productline'
    _description = 'Opportunity Products'

    opportunity_id = fields.Many2one('crm.lead', string='Opportunity')
    product_id = fields.Many2one('product.template', string='Product')
    quantity = fields.Float('Quantity')
    unit_price = fields.Float('Unit Price')
    total_price = fields.Float('Total Price')


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    account_identification = fields.Char(string="Account ID")
    is_auto_quotation = fields.Boolean(string="Is auto Quotation")
    outside_source = fields.Boolean(string="Outside Source", default=False)
    contract_start_date = fields.Date(
        string="Contract Start Date", required=True)
    contract_end_date = fields.Date(string="Contract End Date", required=True)
    plan = fields.Many2one('sale.order.template', string="Plan")
    no_tv = fields.Integer(string="Number of TV")
    internet_speed = fields.Integer(string="Internet Speed")
    device = fields.Many2many('product.product', string="Device")
    cable = fields.Selection([('none', 'None'),
                              ('analog', 'Analog'),
                              ('digital', 'Digital')], string="Cable")
    promo = fields.Boolean(string="Promo")
    has_id = fields.Boolean(string="Has ID")
    has_proof_bill = fields.Boolean(string="Proof of Blling")
    has_lease_contract = fields.Boolean(string="Lease Contract")
    others = fields.Text(string="Others")
    initial_payment = fields.Float(string="Initial Payment")
    or_number = fields.Char(string="OR Number")
    payment_date = fields.Date(string="Date of Payment")
    billing_type = fields.Char(string="Billing Type")
    job_order_status = fields.Selection([('new', 'New'),
                                         ('installation', 'Installation'),
                                         ('activation', 'Activation'),
                                         ('completed', 'Completed'),
                                         ('cancel', 'Cancelled')], string="Job Order Status")
    subscription_status = fields.Selection([('new', 'New'),
                                            ('upgrade', 'Upgrade'),
                                            ('convert', 'Convert'),
                                            ('downgrade', 'Downgrade'),
                                            ('re-contract', 'Re-contract'),
                                            ('pre-termination', 'Pre-Termination'),
                                            ('disconnection', 'Disconnection'),
                                            ('reconnection', 'Reconnection')], default='new', string="Subscription Status")
    product_lines = fields.One2many('crm.lead.productline', 'opportunity_id', string='Products')
