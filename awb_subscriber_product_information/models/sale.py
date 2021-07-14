# -*- coding: utf-8 -*-
from odoo import fields, models


class ExpirationNotice(models.Model):
    _name = 'sale.expiration_notice'
    _description = 'Expiration Notice'

    name = fields.Char(string="Name", index=True, required=True)
    number_of_days = fields.Integer("Number of Days", index=True, required=True)
    description = fields.Text('Description')


class SaleOrder(models.Model):
    _inherit = "sale.order"

    account_identification = fields.Char(string="Account ID")
    outside_sourced = fields.Boolean('Outside Source', default=False)
