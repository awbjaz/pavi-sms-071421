# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError, ValidationError


class SubscriberLocation(models.Model):
    _name = "subscriber.location"
    _description = "Subscriber Location"
    _inherit = ['mail.thread']

    name = fields.Char(string="Location Name", required=True)
    code = fields.Char(string="Code")
    billing_day = fields.Integer(string="Billing Day")
    location_id = fields.Many2one('subscriber.location', string="Parent Location")
    location_type = fields.Selection([('head', 'Head'),
                                      ('cluster', 'Cluster'),
                                      ('area', 'Area'),
                                      ('zone', 'Zone')], default='head', string="Location Type")
    active = fields.Boolean(string="Active", default=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    location_ids = fields.One2many('subscriber.location', 'location_id', string="Child Location")
    project_ids = fields.One2many('project.project', 'subscriber_location_id', string="Project")
    subscription_ids = fields.One2many('sale.subscription', 'subscriber_location_id', string="Subscription")
    subscription_count = fields.Integer(string="Number of Subscription", compute='_compute_subscription')
    description = fields.Text(string="Description")

    cluster_head = fields.Many2one('hr.employee', string="Cluster Head")

    @api.onchange('billing_day')
    def _onchange_billing_day(self):
        if self.billing_day > 31:
            raise UserError(_('Billing Day cannot be exceed the Calendar Day'))

    @api.depends('subscription_ids')
    def _compute_subscription(self):
        for rec in self:
            rec.subscription_count = len(rec.subscription_ids)
