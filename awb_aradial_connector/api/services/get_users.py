from odoo import http
from odoo.http import request
from .authentication import OdooAPI 

import importlib
import json

Serializer = importlib.import_module(
    "odoo.addons.odoo-rest-api"
).controllers.serializers.Serializer

SUBSCRIPTION = "sale.subscription"

class OdooAPI(OdooAPI):

    # Get all users subscription
    @http.route('/awb/get_users/', type='http', auth='user', methods=["GET"], csrf=False)
    def get_users(self, **kwargs):
        return super().get_model_data(SUBSCRIPTION, **kwargs)
