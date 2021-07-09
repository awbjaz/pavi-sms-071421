import json
import requests
from odoo import exceptions


class AradialAPIGateway(object):
    def __init__(
        self,
        url,
        token, 
        data
    ):
        self.url = url

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': token
        }

        self.data = data


    def create_user(self):

        try:
            res = requests.post(
                url=self.url,
                headers=self.headers,
                data=json.dumps(self.data)
            )
        except requests.exceptions.MissingSchema as e:
            raise exceptions.ValidationError(e)

        state = "Success" if res.status_code == 201 else "Fail"

        return state
