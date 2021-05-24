from odoo import api, fields, models, exceptions, _
from string import Formatter
import logging

_logger = logging.getLogger(__name__)


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

    def get_template_format(self, template_name):
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

        # Template format returns Keys from the template
        # for e.g. [partner_id, customer_number, ...]
        template_format = [fkey for _, fkey, _, _ in Formatter().parse(raw_template_body) if fkey]

        return raw_template_body, template_format
