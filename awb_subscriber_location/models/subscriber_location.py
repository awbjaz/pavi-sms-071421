# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError, ValidationError

from datetime import date
from dateutil.relativedelta import relativedelta


class SubscriberLocation(models.Model):
    _name = "subscriber.location"
    _description = "Subscriber Location"
    _inherit = ['mail.thread']

    name = fields.Char(string="Location Name", required=True, tracking=True)
    code = fields.Char(string="Code", tracking=True)
    billing_day = fields.Integer(string="Billing Day", tracking=True)
    posting_day = fields.Integer(string="Posting Day", tracking=True)
    cutoff_day = fields.Integer(string="Cut Off Day", tracking=True)
    billing_due_day = fields.Integer(string="Bill Due Day", tracking=True)
    location_id = fields.Many2one('subscriber.location', string="Parent Location",
                                  tracking=True)
    location_type = fields.Selection([('head', 'Head'),
                                      ('cluster', 'Cluster'),
                                      ('area', 'Area'),
                                      ('zone', 'Zone')], default='head', string="Location Type", tracking=True)
    active = fields.Boolean(string="Active", default=True, tracking=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    location_ids = fields.One2many('subscriber.location', 'location_id', string="Child Location")
    project_ids = fields.One2many('project.project', 'subscriber_location_id', string="Project")
    subscription_ids = fields.One2many('sale.subscription', 'subscriber_location_id', string="Subscription")
    subscription_count = fields.Integer(string="Number of Subscription", compute='_compute_subscription')
    description = fields.Text(string="Description")
    date_started = fields.Date('Activation Date', tracking=True)
    category = fields.Selection([('new', 'New'),
                                 ('existing', 'Existing')], string="Category", compute="_compute_category", tracking=True)
    cluster_head = fields.Many2one('hr.employee', string="Cluster Head", tracking=True)

    def name_get(self):
        data = []
        for rec in self:
            head_name = f"{rec.location_id.location_id.location_id.name} / " if rec.location_id.location_id.location_id else ''
            cluster_name = f"{rec.location_id.location_id.name} / " if rec.location_id.location_id else ''
            area_name = f"{rec.location_id.name} / " if rec.location_id else ''
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
            raise UserError(_('Billing Day cannot exceed the Calendar Day'))

    @api.onchange('posting_day')
    def _onchange_posting_day(self):
        if self.posting_day > 31:
            raise UserError(_('Posting Day cannot exceed the Calendar Day'))

    @api.onchange('cutoff_day')
    def _onchange_cutoff_day(self):
        if self.cutoff_day > 31:
            raise UserError(_('Cutoff Day cannot exceed the Calendar Day'))

    @api.onchange('billing_due_day')
    def _onchange_billing_due_day(self):
        if self.billing_due_day > 31:
            raise UserError(_('Billing Due Day cannot exceed the Calendar Day'))

    @api.depends('subscription_ids')
    def _compute_subscription(self):
        for rec in self:
            rec.subscription_count = len(rec.subscription_ids)

    def _compute_category(self):
        last_year = date.today() - relativedelta(years=1)
        for rec in self:
            if rec.date_started and last_year < rec.date_started:
                rec.category = 'new'
            else:
                rec.category = 'existing'
