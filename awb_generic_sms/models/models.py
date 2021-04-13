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

    def send_now(
        self,
        sms_id=None,
        recipient_ids=None,
        template_body=None,
        record=None,
        template_name=None,
        state=None
    ):
        if record:
            if state and record.state == state:
                recipient_ids = record.partner_id

                raw_template_body = self.env['awb.sms.template'].search(
                    [("name", "=", template_name)], limit=1, order="write_date desc"
                ).template_body

                raw_template_body = raw_template_body.replace("${", "{")
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
                            pass

                    raw_data = {key: value}
                    key_value.update(raw_data)

                template_body = raw_template_body.format_map(key_value)
            else:
                return None

        sms = SendSMS(sms_id=sms_id, recipients=recipient_ids, message=template_body)
        sent_sms = sms.send()
        self.save_history(sent_sms)

    def send_automated_sms(self, target_date, template_name=None, state=None):
        invoices = self.env['account.move'].search(
            [("invoice_date_due", "=", target_date),]
        )
        for invoice in invoices:
            self.env['awb.sms.send'].send_now(
                record=invoice,
                template_name=template_name,
                state=state
            )

    def send_billing_reminder(self, template_name=None, state=None):
        today = datetime.date.today()
        target_date = today + datetime.timedelta(days=3)
        self.send_automated_sms(
            target_date=target_date,
            template_name=template_name,
            state=state,
        )

    def send_disconnection_notice(self, template_name=None, state=None):
        today = datetime.date.today()
        target_date = today - datetime.timedelta(days=3)
        self.send_automated_sms(
            target_date=target_date,
            template_name=template_name,
            state=state,
        )

    def send_actual_disconnection_notice(self, template_name=None, state=None):
        today = datetime.date.today()
        target_date = today - datetime.timedelta(days=7)
        self.send_automated_sms(
            target_date=target_date,
            template_name=template_name,
            state=state,
        )


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

    name = fields.Char("Name", readonly=True)
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

    @api.model
    def _default_body(self):
        msg_body = """
            Good day!,
            This is your bill for the month of ${billing_month},
            Accnt Name: ${account_name},
            Accnt No.: ${account_num},
            MSF: ${msf_php},
            Arrears: ${arrears},
            Total Bill: ${total_bill},
            ATM Ref No.: ${atm_ref_no},
            Bill No.: ${bill_num},
            Due Date: ${due_date},
            Bill Covered: ${bill_covered}

            You may now pay your bill via this link, https://www.streamtech.com.ph/bills-payment/
            Please use your ATM.
            Thank you.
        """
        return msg_body

    template_body = fields.Text('Message', translate=True, default=_default_body)
