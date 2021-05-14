from odoo import api, fields, models, exceptions, _
import logging

_logger = logging.getLogger(__name__)

class InheritAccountMove(models.Model):
    _inherit = "account.move"

    receive_sms = fields.Boolean(string="Active", default=True)

    @api.model
    def show_skip_sms(self, records):
        if records:
        	rec_msg = '- ' + ' \n - '.join(
        		records.mapped('display_name')
        	)
        	raise exceptions.Warning(
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

    def send_autoinvoice_sms(
        self,
        payment_date_criteria=None,
        due_date_criteria=None,
        template_name=None,
        state=None,
        model=None,
        allow_partial_payment=False,
        limit=None,
        send_only_to_active=None,
        disconnection_subtype=None,
        **kwargs
    ):
        self.env['awb.sms.send'].send_auto_sms(
            due_date_criteria=due_date_criteria,
            template_name=template_name,
            state=state,
            model='account.move',
            limit=limit,
            send_only_to_active=send_only_to_active,
            allow_partial_payment=allow_partial_payment,
            disconnection_subtype=disconnection_subtype,
            **kwargs,
        )
