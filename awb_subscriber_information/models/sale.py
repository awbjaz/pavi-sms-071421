# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    account_identification = fields.Char(string="Account ID")


class ExpirationNotice(models.Model):
    _name = 'sale.expiration_notice'

    name = fields.Char(string="Name", index=True, required=True)
    number_of_days = fields.Integer("Number of Days", index=True, required=True)
    description = fields.Text('Description')
