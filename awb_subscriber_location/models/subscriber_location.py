# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models


class SubscriberLocation(models.Model):
    _name = "subscriber.location"
    _description = "Subscriber Location"
    _inherit = ['mail.thread']

    name = fields.Char(string="Location Name", required=True)
    code = fields.Char(string="Code")
    location_id = fields.Many2one('subscriber.location', string="Parent Location")
    location_type = fields.Selection([('head', 'Head'),
                                      ('cluster', 'Cluster'),
                                      ('area', 'Area'),
                                      ('zone', 'Zone')], default='head', string="Location Type")
    active = fields.Boolean(string="Active", default=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    location_ids = fields.One2many('subscriber.location', 'location_id', string="Child Location")
    description = fields.Text(string="Description")

    cluster_head = fields.Many2one('hr.employee', string="Cluster Head")
