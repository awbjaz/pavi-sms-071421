from odoo import api, fields, models, exceptions, _
import logging

_logger = logging.getLogger(__name__)


class SmsDeactivate(models.Model):
    _name = 'awb.sms.deactivate'
    _description = 'SMS Sending Deactivate'

    def bulk_deactivate_sms_sending(self, limit=20000):
        _logger.debug("Start: Bulk deactivation of SMS Sending")
        models = [
            'account.move',
            'account.payment'
        ]
        for model in models:
            records = self.env[model].search([("receive_sms", "=", True)], limit=limit)
            if records.exists():
                records.write({"receive_sms": False})
                _logger.debug("Deactivated %s records" % len(records))
