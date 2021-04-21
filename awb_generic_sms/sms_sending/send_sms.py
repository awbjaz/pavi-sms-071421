import json
import requests
from odoo import exceptions
from ..models import models


class SendSMS(object):
    def __init__(
        self,
        url,
        token,
        sms_id,
        recipients,
        message,
        recordsets=None,
        sms_gateway=None,
        auth=None
    ):
        self.headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': token
        }
        self.recipients = recipients
        self.message = message
        self.sms_id = sms_id
        self.url = url

    def send(self):
        sms_data = []
        for recipient in self.recipients:
            data = {
                'messageType': 'sms',
                'destination': recipient.mobile,
                'text': self.message,
            }
            try:
                res = requests.post(
                    url=self.url,
                    headers=self.headers,
                    data=json.dumps(data)
                )
            except requests.exceptions.MissingSchema as e:
                raise exceptions.ValidationError(e)

            state = "sent" if res.status_code == 201 else "failed"
            sms_data.append(
                {
                    "recipient_id": recipient.id,
                    "name": "%s (%s)" % (
                        recipient.mobile if recipient.mobile else "No mobile number", state.title()
                    ),
                    "status_code": res.status_code,
                    "sms_id": self.sms_id,
                    "state": state,
                    "message": self.message
                }
            )
        return sms_data
