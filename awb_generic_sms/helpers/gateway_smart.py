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
        source=None,
        template_name=None,
        sms_history=None,
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
        self.source = source
        self.sms_history = sms_history

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
            status_code = None
            if record.get("has_invalid_field"):
                state = "failed_invalid"
            else:
                res = self.send_sms_now(
                    message_type='sms',
                    destination=record["mobile"],
                    text=record['template_body']
                )
                status_code = res.status_code
                state = "sent" if status_code == 201 else "failed"

            state_label = dict(self.sms_history._fields['state'].selection)[state]

            # Audit Trail for SMS sending
            if record['record'] and hasattr(record['record'], 'message_post'):
                message = """
                    <p>
                        SMS: <strong>%s</strong>
                    </p>
                    <p>Status: <strong>%s</strong></p>
                """ % (
                    self.template_name, state_label
                )

                record['record'].message_post(body=message)

            if record['record']:
                record_model = record['record']._name
                record_id = record['record'].id

            sms_data.append(
                {
                    "recipient_id": record['partner_id'],
                    "name": "%s" % (
                        record['mobile'] if record['mobile'] else "No mobile number"
                    ),
                    "status_code": status_code,
                    "state": state,
                    "message": record['template_body'],
                    "record_model": record_model,
                    "record_id": record_id,
                    "message_type": self.template_name,
                    "source": self.source,
                }
            )
        return sms_data
