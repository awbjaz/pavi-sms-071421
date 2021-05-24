from odoo import api, fields, models, exceptions, _
import logging

_logger = logging.getLogger(__name__)


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
    record_model = fields.Char("Record Model", readonly=True)
    record_id = fields.Integer("Record Id", readonly=True)
    display_record = fields.Html("Record", compute='_get_display_record')
    message_type = fields.Char("Message Type", readonly=True)

    @api.depends('record_model', 'record_id')
    def _get_display_record(self):
        for rec in self:
            record = None
            if rec.record_model and rec.record_id:
                record_object = self.env[rec.record_model].browse([rec.record_id])
                record = "<a href='#id=%s&model=%s' name='display_record'><span>%s</span></a>" % (
                    rec.record_id,
                    rec.record_model,
                    record_object.name
                )
            rec.display_record = record
