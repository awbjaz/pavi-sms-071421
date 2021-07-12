from odoo import http
from odoo.http import request

import importlib
import json


OdooAPI = importlib.import_module(
    "odoo.addons.odoo-rest-api"
).controllers.controllers.OdooAPI

Serializer = importlib.import_module(
    "odoo.addons.odoo-rest-api"
).controllers.serializers.Serializer

AWB_API = [
    "get_users",
    "disconnect_users",
    "get_users_status",
]

class OdooAPI(OdooAPI):

    @http.route('/awb/', type='http', auth='none', methods=["GET"], csrf=False)
    # if auth='user' this is with params, or session_id token
    # if auth='none', can access with login token
    # res = requests.get(URL, params=params)
    def _check_auth(self, *args, **kwargs):
        api_lists = ""
        if (
            request.auth_method
            and request.session.get("login")
            and request.session.get("session_token")
        ):
            for api in AWB_API:
                api_lists += "<li>/awb/%s</li>\n" % api

            html = """
                <div>
                    <strong>AWB API list:</strong>
                    <ul>%s</ul>
                </div>

            """ % api_lists

            return http.Response(
                html,
                status=200,
                mimetype="text/html"
            )
        else:
            res = {
              "errors": [
                {
                  "status": 401,
                  "message": "Unauthorized'",
                  "code": 352,
                  "description": "",
                  "links": {
                    "about": "http://www.domain.com/rest/errorcode/352"
                  },
                  "data": {},
                  "data_count": {},
                }
              ]
            }

            return json.dumps(res)
