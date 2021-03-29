# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models
from odoo.exceptions import Warning, UserError, ValidationError


class AwbApprovalCategory(models.Model):
    _inherit = "approval.category"

    has_products = fields.Selection([('required', 'Required'),
                                     ('optional', 'Optional'),
                                     ('no', 'None')],
                                    default='no', string="Products", required=True)
    has_analytic_account = fields.Selection([('required', 'Required'),
                                             ('optional', 'Optional'),
                                             ('no', 'None')],
                                            default='no',
                                            string="Analytic Account",
                                            required=True)

    has_application = fields.Selection([('required', 'Required'),
                                        ('default', 'Default'),
                                        ('no', 'None')],
                                       default='no', string="Application", required=True)
    application_type = fields.Selection([], string='Application Type')
    prefix = fields.Char(string='Prefix', default='', required=True)
