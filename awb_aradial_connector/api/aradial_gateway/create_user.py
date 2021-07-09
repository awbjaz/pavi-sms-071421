import json
import requests
from odoo import exceptions
from requests.auth import HTTPBasicAuth

import logging

_logger = logging.getLogger(__name__)

class AradialAPIGateway(object):
    def __init__(
        self,
        url,
        username,
        password,
        data
    ):

        _logger.info("URL [%s]" % url)
        _logger.info("data [%s]" % data)
        _logger.info("username [%s]" % username)
        _logger.info("password [%s]" % password)

        self.url = url
        self.username = username
        self.password = password

        self.headers = {
            'Content-Type': 'application/json'
        }
        _logger.info("headers [%s]" % self.headers)

        self.data = data


    def create_user(self):

        try:
            res = requests.post(
                url=self.url,
                headers=self.headers,
                data=json.dumps(self.data),
                auth=HTTPBasicAuth(self.username, self.password)
            )
        except requests.exceptions.MissingSchema as e:
            raise exceptions.ValidationError(e)

        state = "Success" if res.status_code == 201 else "Fail"
        _logger.info("response [%s]" % res)



        return state
