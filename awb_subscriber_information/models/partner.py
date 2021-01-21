# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models
from datetime import date

import logging

_logger = logging.getLogger(__name__)


class PartnerAccountClassification(models.Model):
    _name = 'partner.classification'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')


class PartnerServiceProvider(models.Model):
    _name = 'partner.service.provider'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')


class Partner(models.Model):
    _inherit = "res.partner"

    last_name = fields.Char(string="Last Name")
    first_name = fields.Char(string="First Name")
    middle_name = fields.Char(string="Middle Name")
    birthday = fields.Date(string="Birthday")
    age = fields.Char(string="Age", compute="_compute_age")
    civil_status = fields.Selection([('single', 'Single'),
                                     ('married', 'Married'),
                                     ('separated', 'Legally Separated')], string="Civil Status")
    home_ownership = fields.Selection([('owned', 'Owned'),
                                       ('rented', 'Rented'),
                                       ('living_relatives',
                                        'Living with Relatives'),
                                       ('company_provide', 'Company Provided'),
                                       ('mortgaged', 'Mortgaged')], string="Home Ownership")
    account_classification = fields.Selection([('internal', 'Affiliate / Internal'),
                                               ('external', 'External')], string="Account Classification")
    account_subclassification = fields.Many2one('partner.classification', string='Account Subclassification')
    subscriber_type = fields.Selection([('enterprise', 'Enterprise'),
                                        ('sme', 'SME'),
                                        ('internal', 'Internal'),
                                        ('msme', 'MSME')], string='Subscriber Type')
    account_group = fields.Selection([('vista', 'Vista'),
                                     ('non-vista', 'Non-Vista')], string='Account Group')
    account_type = fields.Selection([('corporate', 'Corporate'),
                                     ('mail_tenant', 'Mail-Tenant'),
                                     ('sme', 'SME')], string='Type')
    brand = fields.Many2one('project.brand', string="Brand")
    service_provider = fields.Many2one('partner.service.provider', string="Service Provider")
    expiration_notice = fields.Many2one('sale.expiration_notice', string="Expiration Notice")

    @api.onchange('last_name', 'first_name', 'middle_name')
    def _onchange_name(self):
        self.name = (self.first_name or '') + ' ' + \
            (self.middle_name or '') + ' ' + str(self.last_name or '')

    def _compute_age(self):
        age = 0
        today = date.today()
        if self.birthday:
            bday = self.birthday
            age = today.year - bday.year - ((today.month, today.day) < (bday.month, bday.day))

        self.age = age
        _logger.debug(f'Age {self.age}')
