# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models


class CRMLead(models.Model):
    _inherit = "crm.lead"

    account_identification = fields.Char(string="Account ID")
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
    has_id = fields.Boolean(string="ID")
    has_proof_bill = fields.Boolean(string="Proof of Blling")
    has_lease_contract = fields.Boolean(string="Lease Contract")
    others = fields.Text(string="Others")
    initial_payment = fields.Float(string="Initial Payment")
    or_number = fields.Text(string="OR Number")
    payment_date = fields.Date(string="Date of Payment")
    billing_type = fields.Text(string="Billing Type")
