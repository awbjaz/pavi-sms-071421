from ..api.aradial_gateway.create_user import AradialAPIGateway
from odoo import api, fields, models, exceptions, _
from psycopg2.extensions import AsIs
import datetime
import logging

_logger = logging.getLogger(__name__)

class AWBAradialConnector(models.Model):

    _name = 'awb.aradial.connector'
    _description = 'AWB Aradial Connector'

    def create_user(
        self, 
        data
    ):

        _logger.info("Create User")

        params = self.env['ir.config_parameter'].sudo()
        aradial_url = params.get_param('aradial_url')
        aradial_token = params.get_param('aradial_token')

        _logger.info("Calling API %s" % aradial_url)
        
        user = AradialAPIGateway(
            url=aradial_url,
            token=aradial_token,
            data=data
        )
        created_user = user.create_user()

        _logger.info("User Creation: %s" % created_user)
    