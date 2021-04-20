# -*- coding: utf-8 -*-

from ..sms_sending.send_sms import SendSMS
from odoo import api, fields, models, exceptions, _
from string import Formatter
import datetime
import logging

_logger = logging.getLogger(__name__)


class SMS(models.Model):
    _name = 'awb.sms.send'
    _description = 'SMS Sending'

    def save_history(self, sent_sms):
        self.env['awb.sms.history'].create(sent_sms)

    def _check_sms_gateway(
        self,
        sms_gateway,
        sms_gateway_url,
        sms_gateway_token,
    ):
        if sms_gateway:
            error = []
            if not sms_gateway_url:
                error.append("SMS Gateway Url")
            if not sms_gateway_token:
                error.append("SMS Gateway Token")
            if error:
                raise exceptions.ValidationError(
                    ("%s is/are not set, You can configure this on Settings > Smart SMS Gateway") % (
                        ", ".join(error)
                    )
                )
        else:
            raise exceptions.ValidationError(
                "Inactive SMS Gateway, You can configure this on Settings > Smart SMS Gateway"
            )

    def send_now(
        self,
        sms_id=None,
        recipient_ids=None,
        template_body=None,
        record=None,
        template_name=None,
        state=None
    ):
        params = self.env['ir.config_parameter'].sudo()
        sms_gateway = params.get_param('smart_gateway')
        sms_gateway_url = params.get_param('smart_gateway_url')
        sms_gateway_token = params.get_param('smart_gateway_token')

        self._check_sms_gateway(
            sms_gateway,
            sms_gateway_url,
            sms_gateway_token,
        )

        if record:
            if not state:
                raise exceptions.ValidationError(
                    ("State parameter is required, Please check server actions")
                )
            if record.state == state:
                recipient_ids = record.partner_id

                raw_template_body = self.env['awb.sms.template'].search(
                    [("name", "=", template_name)], limit=1, order="write_date desc"
                )

                if raw_template_body.exists():
                    raw_template_body = raw_template_body.template_body.replace("${", "{")
                else:
                    raise exceptions.ValidationError(
                        (
                            "SMS Template %s not found, Make sure to input the correct SMS Template name"
                        ) % template_name
                    )

                format_keys = [fkey for _, fkey, _, _ in Formatter().parse(raw_template_body) if fkey]

                key_value = {}
                for key in format_keys:

                    try:
                        value = getattr(record, key)
                    except AttributeError:
                        value = None

                    if value:
                        try:
                            if value.name:
                                value = value.name
                        except AttributeError:
                            if isinstance(value, float):
                                value = "\u20B1 {:,.2f}".format(value)
                            else:
                                pass

                    raw_data = {key: value}
                    key_value.update(raw_data)

                template_body = raw_template_body.format_map(key_value)
            else:
                raise exceptions.ValidationError(
                    ("Record should be in %s state.") % state
                )

        sms = SendSMS(
            url=sms_gateway_url,
            token=sms_gateway_token,
            sms_id=sms_id,
            recipients=recipient_ids,
            message=template_body
        )
        sent_sms = sms.send()
        self.save_history(sent_sms)

    def send_autoinvoice_sms(self, due_date_criteria=None, template_name=None, state=None):
        if not state:
            raise exceptions.ValidationError(
                ("State parameter is required")
            )

        invoices = self.env['account.move'].search(
            [("state", "=", state)]
        )
        if due_date_criteria:
            today = datetime.date.today()
            due_date_criteria = today + datetime.timedelta(days=due_date_criteria)
            invoices = invoices.search(
                [("invoice_date_due", "=", due_date_criteria),]
            )
        
        for invoice in invoices:
            self.env['awb.sms.send'].send_now(
                record=invoice,
                template_name=template_name,
                state=state
            )

    def send_autopayment_sms(self, due_date_criteria=None, template_name=None, state=None):
        return None


class SmsRecord(models.Model):
    _name = "awb.sms.record"
    _description = "SMS Record"
    _order = 'create_date desc'

    name = fields.Char(string="SMS Record", compute='_compute_sms_name')
    user_id = fields.Many2one(
        'res.users', 'Sender',
        default=lambda self: self.env.user,
        index=True, required=True, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent','Sent'),
        ('cancel','Cancel'),
        ], string='State', default='draft')
    account_id = fields.Many2one('sms.api.configuration', 'SMS Gateway')
    template_id = fields.Many2one('awb.sms.template', 'SMS Template')
    template_body = fields.Text('Message', translate=True, help="SMS Template")
    recipient_ids = fields.Many2many('res.partner', string='Recipients')

    @api.depends('create_date')
    def _compute_sms_name(self):
        for rec in self:
            rec.name = "SMS %s" % rec.create_date.strftime(
                "%b %d, %Y - %I:%M %p"
            )

    def send_now(self):
        self.env['awb.sms.send'].send_now(
            sms_id=self.id,
            recipient_ids=self.recipient_ids,
            template_body=self.template_body,
        )
        self.state = "sent"


class SmsHistory(models.Model):
    _name = 'awb.sms.history'
    _description = 'SMS History'
    _order = 'create_date desc'

    name = fields.Char("Recipient", readonly=True)
    recipient_id = fields.Many2one('res.partner', string='Name')
    sms_id = fields.Many2one('awb.sms.record', 'SMS Record', readonly=True)
    state = fields.Selection([
        ('failed', 'Failed'),
        ('sent','Sent'),
        ], string='Sending State', default='failed', readonly=True)
    status_code = fields.Char('Status Code', readonly=True)
    message = fields.Text('Message', translate=True, help="SMS Message", readonly=True)


class SmsTemplate(models.Model):
    _name = 'awb.sms.template'
    _description = 'SMS Template'
    _order = 'write_date desc'

    name = fields.Char(string="Name", required=True)
    template_model = fields.Selection(
        [('billing', 'Billing'),],
        string="Model", required=True, default="billing"
    )

    template_body = fields.Text('Message', translate=True)
