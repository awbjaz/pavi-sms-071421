import json
import requests
from odoo import exceptions

import logging

_logger = logging.getLogger(__name__)

class AradialAPIGateway(object):
    def __init__(
        self,
        url,
        token, 
        data
    ):

        _logger.info("URL [%s]" % url)
        _logger.info("Token [%s]" % url)
        _logger.info("data [%s]" % data)

        self.url = url

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': token
        }
        _logger.info("headers [%s]" % self.headers)

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
