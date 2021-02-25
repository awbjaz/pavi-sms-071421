# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
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
    device_fee = fields.Float(string="Device Fee", default=0)
    unit_price = fields.Float('Unit Price')
    total_price = fields.Float('Total Price')


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    account_identification = fields.Char(string="Account ID")
    company_type = fields.Selection(related="partner_id.company_type", string="Account Type")
    is_auto_quotation = fields.Boolean(string="Is auto Quotation")
    outside_source = fields.Boolean(string="Outside Source", default=False)
    contract_start_date = fields.Date(string="Contract Start Date", required=False)
    contract_end_date = fields.Date(string="Contract End Date", required=False)
    contract_term = fields.Integer(string="Contract Term")
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
    zone = fields.Many2one('subscriber.location', domain=[('location_type', '=', 'zone')], string="Zone")
    category = fields.Selection(related='zone.category', string="Category")

    def write(self, vals):
        is_completed = self.env.ref('awb_subscriber_product_information.stage_completed')
        _logger.debug(f'stage {is_completed} current {self.stage_id} {vals}')
        if 'stage_id' in vals and vals["stage_id"] == is_completed.id:
            if not self.zone:
                raise UserError(_('Please specify zone.'))

        write_result = super(CRMLead, self).write(vals)

        return write_result

    @api.onchange('zone')
    def _onchange_zone(self):
        _logger.debug(f'Change Zone: {self.zone}')
        if self.partner_id:
            self.partner_id.subscriber_location_id = self.zone.id

    @api.onchange('partner_id')
    def _onchange_partner(self):
        _logger.debug(f'Change Partner: {self.partner_id}')
        if self.partner_id and self.partner_id.subscriber_location_id:
            self.zone = self.partner_id.subscriber_location_id.id
