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
    location_id = fields.Many2one(
        'subscriber.location', string="Parent Location")
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
    date_started = fields.Date('Launch Date')
    category = fields.Selection([('new', 'New'),
                                 ('existing', 'Existing')], string="Category")
    cluster_head = fields.Many2one('hr.employee', string="Cluster Head")

    def name_get(self):
        data = []
        for rec in self:
            head_name = f"{rec.location_id.location_id.location_id.name}/" if rec.location_id.location_id.location_id else ''
            cluster_name = f"{rec.location_id.location_id.name}/" if rec.location_id.location_id else ''
            area_name = f"{rec.location_id.name}/" if rec.location_id else ''
            name = rec.name
            display_value = f"{head_name}{cluster_name}{area_name}{name}"
            data.append((rec.id, display_value))
        return data

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        res = super(SubscriberLocation, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
        if name:
            records = self.search(
                ['|', '|', '|', ('name', operator, name), ('location_id.name', operator, name), ('location_id.location_id.name', operator, name), ('location_id.location_id.location_id.name', operator, name)])
            return records.name_get()
        return res

    @api.onchange('billing_day')
    def _onchange_billing_day(self):
        if self.billing_day > 31:
            raise UserError(_('Billing Day cannot be exceed the Calendar Day'))

    @api.depends('subscription_ids')
    def _compute_subscription(self):
        for rec in self:
            rec.subscription_count = len(rec.subscription_ids)
