import json
import requests
from ..models import models

SMART_API_URL = 'https://messagingsuite.smart.com.ph/cgpapi/messages/sms'
SMART_AUTH = 'Basic amVycnkubWFycXVlc2VzQG1hbmRhbGF5LmNvbS5waDpwNGpOZ0w5Uw=='


class SendSMS(object):
    def __init__(self, sms_id, recipients, message, recordsets=None, sms_gateway=None, auth=None):
        self.headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': SMART_AUTH
        }
        self.recipients = recipients
        self.message = message
        self.sms_id = sms_id

    def send(self):
        sms_data = []
        recipients_mobile = self.recipients.mapped('mobile')
        for mobile_num in recipients_mobile:
            data = {
                'messageType': 'sms',
                'destination': mobile_num,
                'text': self.message,
            }
            res = requests.post(
                url=SMART_API_URL,
                headers=self.headers,
                data=json.dumps(data)
            )
            state = "sent" if res.status_code == 201 else "failed"
            sms_data.append(
                {
                    "name": "%s (%s)" % (
                        mobile_num if mobile_num else "No mobile number", state.title()
                    ),
                    "status_code": res.status_code,
                    "sms_id": self.sms_id,
                    "state": state,
                    "message": self.message
                }
            )
        return sms_data
