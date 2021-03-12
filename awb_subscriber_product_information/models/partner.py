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
    _description = 'Partner Classification'

    name = fields.Char('Name', required=True)
    account_classification = fields.Selection([('internal', 'Affiliate / Internal'),
                                               ('external', 'External')], string="Account Classification")
    description = fields.Text('Description')


class PartnerServiceProvider(models.Model):
    _name = 'partner.service.provider'
    _description = 'Service Provider'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')


class Partner(models.Model):
    _inherit = "res.partner"

    customer_number = fields.Char(string='Customer ID')
    customer_number_old = fields.Char(string='Customer ID (Old)')
    last_name = fields.Char(string="Last Name")
    first_name = fields.Char(string="First Name")
    middle_name = fields.Char(string="Middle Name")
    birthday = fields.Date(string="Birthday")
    age = fields.Char(string="Age", compute="_compute_age")
    gender = fields.Selection([('male', 'Male'),
                               ('female', 'Female'),
                               ('others', 'Others')])
    civil_status = fields.Selection([('single', 'Single'),
                                     ('married', 'Married'),
                                     ('separated', 'Legally Separated'),
                                     ('others', 'Others')], string="Civil Status")
    home_ownership = fields.Selection([('owned', 'Owned'),
                                       ('rented', 'Rented'),
                                       ('living_relatives', 'Living with Relatives'),
                                       ('company_provided', 'Company Provided'),
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
                                     ('mall_tenant', 'Mall-Tenant'),
                                     ('sme', 'SME')], string='Type')
    zone_type = fields.Selection([('vista', 'Vista'),
                                  ('non-vista', 'Non-Vista')], string='Zone Type')
    zone_subtype = fields.Many2one('zone.subtype', string='Zone Subtype')
    service_provider = fields.Many2one('partner.service.provider', string="Service Provider")
    expiration_notice = fields.Many2one('sale.expiration_notice', string="Expiration Notice")
    outside_sourced = fields.Boolean('Outside Source', default=False)

    @api.onchange('last_name', 'first_name', 'middle_name')
    def _onchange_name(self):
        vals = {}
        if self.company_type == 'person':
            name = ''
            if self.first_name:
                name += self.first_name + ' '
            if self.middle_name:
                name += self.middle_name + ' '
            if self.last_name:
                name += self.last_name

            vals.update({'name': name})

        self.write(vals)

    def action_assign_customer_id(self):
        for rec in self:
            if rec.customer_rank > 0 and not rec.customer_number:
                cust_no = rec.env['ir.sequence'].next_by_code('subscriber.customer.id')
                rec.update({'customer_number': cust_no})

    def _compute_age(self):
        age = 0
        today = date.today()
        if self.birthday:
            bday = self.birthday
            age = today.year - bday.year - ((today.month, today.day) < (bday.month, bday.day))

        self.age = age
        _logger.debug(f'Age {self.age}')
