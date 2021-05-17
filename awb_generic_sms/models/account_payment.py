from odoo import api, fields, models, exceptions, _
import logging

_logger = logging.getLogger(__name__)

class InheritAccountPayment(models.Model):
    _inherit = "account.payment"

    receive_sms = fields.Boolean(string="Active", default=True)

    @api.model
    def show_skip_sms(self, records):
        # Display all skipped records
        if records:
            rec_msg = '- ' + ' \n - '.join(
                records.mapped('display_name')
            )
            raise exceptions.ValidationError(
                """Sending SMS to these invoices is/are disabled:
                \n %s \n\n You can set SMS Sending to Active on Record > Other Info tab"""
                % rec_msg
            )

    @api.model
    def activate_sms_sending(self, records):
        records.write({"receive_sms": True})

    @api.model
    def deactivate_sms_sending(self, records):
        records.write({"receive_sms": False})

    def send_autopayment_sms(
        self,
        payment_date_criteria=None,
        template_name=None,
        state=None,
        model=None,
        limit=None,
        send_only_to_active=None,
        disconnection_subtype=None,
        **kwargs,
    ):
        self.env['awb.sms.send'].send_auto_sms(
            payment_date_criteria=payment_date_criteria,
            template_name=template_name,
            state=state,
            model='account.payment',
            limit=limit,
            send_only_to_active=send_only_to_active,
            disconnection_subtype=disconnection_subtype,
            **kwargs,
        )
