import json
import requests
from odoo import exceptions


class SmartAPIGateway(object):
    def __init__(
        self,
        url,
        token,
        sms_id,
        recordset=None,
        sms_gateway=None,
        auth=None,
        record=None,
        template_name=None,
    ):
        self.headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': token
        }

        if not recordset:
            return None

        self.recordset = recordset
        self.sms_id = sms_id
        self.url = url
        self.template_name = template_name

    def send_sms_now(
        self,
        message_type='sms',
        destination=None,
        text=None,
    ):
        data = {
            'messageType': message_type,
            'destination': destination,
            'text': text
        }

        try:
            res = requests.post(
                url=self.url,
                headers=self.headers,
                data=json.dumps(data)
            )
        except requests.exceptions.MissingSchema as e:
            raise exceptions.ValidationError(e)
        return res

    def send(self):
        sms_data = []
        for record in self.recordset:
            res = self.send_sms_now(
                message_type='sms',
                destination=record["mobile"],
                text=record['template_body']
            )

            state = "sent" if res.status_code == 201 else "failed"

            # Audit Trail for SMS sending
            if record['record'] and hasattr(record['record'], 'message_post'):
                message = """
                    <p>
                        SMS: <strong>%s</strong>
                    </p>
                    <p>Status: <strong>%s</strong></p>
                """ % (
                    self.template_name, state.title()
                )

                record['record'].message_post(body=message)

            if record['record']:
                record_model = record['record']._name
                record_id = record['record'].id

            sms_data.append(
                {
                    "recipient_id": record['partner_id'],
                    "name": "%s (%s)" % (
                        record['mobile'] if record['mobile'] else "No mobile number", state.title()
                    ),
                    "status_code": res.status_code,
                    "state": state,
                    "message": record['template_body'],
                    "record_model": record_model,
                    "record_id": record_id,
                    "message_type": self.template_name,
                }
            )
        return sms_data
