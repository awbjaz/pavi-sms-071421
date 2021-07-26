from odoo import api, fields, models, exceptions, _
import logging

_logger = logging.getLogger(__name__)


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
    template_id = fields.Many2one('awb.sms.template', 'SMS Template')
    template_body = fields.Text('Message', translate=True, help="SMS Template")
    recipient_ids = fields.Many2many('res.partner', string='Recipients')

    location_ids = fields.Many2many(
        'subscriber.location',
        string="Location",
    )

    @api.depends('create_date')
    def _compute_sms_name(self):
        for rec in self:
            rec.name = "SMS %s" % rec.create_date.strftime(
                "%b %d, %Y - %I:%M %p"
            )

    @api.onchange('location_ids')
    def _set_users_per_location(self):
        for rec in self:
            locations = [location._origin.id for location in rec.location_ids]
            recipients = self.env['res.partner'].search(
                [("subscriber_location_id", "in", locations),]
            )
            rec.recipient_ids += recipients

    def clear_field_values(self):
        self.recipient_ids = False
        self.location_ids = False

    def send_now(self):
        # Generic SMS Sending
        data_recordset = []
        for recipient in self.recipient_ids:
            data_recordset.append(
                {
                    "record": self,
                    "mobile": recipient.mobile,
                    "template_body": self.template_body,
                    "partner_id": recipient.id
                }
            )
        self.env['awb.sms.send'].send_now(
            sms_id=self,
            recordset=data_recordset,
            send_type="generic"
        )
        self.state = "sent"