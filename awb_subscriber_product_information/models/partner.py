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

ACCOUNT_CLASSIFICATION = [('internal', 'Affiliate / Internal'),
                          ('external', 'External'),
                          ('avg - allday retail','AVG - Allday Retail'),
                          ('avg - allhome','AVG - Allhome'),
                          ('avg - cmstar management','AVG - CMStar Management'),
                          ('avg - family shoppers','AVG - Family Shoppers'),
                          ('avg - cafe voila','AVG - Cafe Voila'),
                          ('avg - others','AVG - Others'),
                          ('avg - vitacare','AVG - Vitacare'),
                          ('mall - admin office','Mall - Admin Office'),
                          ('mall - managed wifi','Mall - Managed Wifi'),
                          ('parallax','Parallax'),
                          ('vista','Vista'),
                          ('avg - allday marts','AVG - Allday Marts'),
                          ('mark\'s fitness','Mark\'s Fitness'),
                          ('mgs / mex','MGS / MEX'),
                          ('pavi','PAVI'),
                          ('globalland / gets','Globalland / GETs'),
                          ('vip','VIP'),
                          ('franchise','Franchise'),
                          ('allbank','Allbank'),
                          ('georgia academy','Georgia Academy'),
                          ('others','Others'),
                          ('mella hotel','Mella Hotel'),
                          ('golden haven','Golden Haven'),
                          ('enterprise','Enterprise'),
                          ('b2b','B2B'),
                          ('sme','SME'),
                          ('msme','MSME'),
                          ('starmall alabang','Starmall Alabang'),
                          ('starmall edsa-shaw','Starmall EDSA-SHAW'),
                          ('vistamall antipolo (mille luce)','VistaMall Antipolo (Mille Luce)'),
                          ('vistamall bataan','VistaMall Bataan'),
                          ('vistamall cebu (talisay) (azienda)*','VistaMall Cebu (Talisay) (Azienda)*'),
                          ('vistamall daang hari','VistaMall Daang Hari'),
                          ('vistamall dasma (agustine grove)','VistaMall Dasma (Agustine Grove)'),
                          ('vistamall gen trias','VistaMall Gen Trias'),
                          ('vistamall iloilo','VistaMall Iloilo'),
                          ('vistamall lakefront (boardwalk)','VistaMall Lakefront (Boardwalk)'),
                          ('vistamall lakefront (wharf)','VistaMall Lakefront (Wharf)'),
                          ('vistamall las pinas','VistaMall Las Pinas'),
                          ('vistamall las pinas annex','VistaMall Las Pinas Annex'),
                          ('vistamall malolos','VistaMall Malolos'),
                          ('vistamall naga','VistaMall Naga'),
                          ('vistamall nomo','VistaMall NOMO'),
                          ('vistamall pampanga (paseo)','VistaMall Pampanga (Paseo)'),
                          ('vistamall sjdm bulacan','VistaMall SJDM Bulacan'),
                          ('vistamall sta. rosa','VistaMall Sta. Rosa'),
                          ('vistamall taguig','VistaMall Taguig'),
                          ('vistamall tanza','VistaMall Tanza'),
                          ('evia lifestyle center','EVIA Lifestyle Center'),
                          ('mintal davao','Mintal Davao'),
                          ('gran europa','Gran Europa'),
                          ('polar (beside edsa shaw)','Polar (beside EDSA Shaw)'),
                          ('ferrari','Ferrari'),
                          ('bcda commercial pad taguig','BCDA COMMERCIAL PAD TAGUIG'),
                          ('vistamall vibal','VistaMall Vibal'),
                          ('vistahub molino','VistaHub Molino'),
                          ('vistamall las pinas b3','VistaMall Las Pinas B3'),
                          ('wordlwide corporate center','Wordlwide Corporate Center'),
                          ('vistamall silang','VistaMall Silang'),
                          ('vistamall imus','VistaMall Imus'),
                          ('vistamall kawit','VistaMall Kawit'),
                          ('vistamall global south','VistaMall Global South'),
                          ('vistamall cabanatuan','VistaMall Cabanatuan'),
                          ('vistamall sta. maria bulacan','VistaMall Sta. Maria Bulacan')]


class PartnerAccountClassification(models.Model):
    _name = 'partner.classification'
    _description = 'Partner Classification'

    name = fields.Char('Name', required=True)
    account_classification = fields.Selection(ACCOUNT_CLASSIFICATION, string="Account Classification")
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
    account_classification = fields.Selection(ACCOUNT_CLASSIFICATION, string="Account Classification")
    account_subclassification = fields.Many2one('partner.classification', string='Account Subclassification')
    subscriber_type = fields.Selection([('enterprise', 'Enterprise'),
                                        ('sme', 'SME'),
                                        ('internal', 'Internal'),
                                        ('msme', 'MSME'),
                                        ('external', 'External'),
                                        ('mall tenants', 'Mall Tenants')], string='Subscriber Type')
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
