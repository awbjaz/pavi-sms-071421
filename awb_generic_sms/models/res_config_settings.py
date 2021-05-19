# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class AWBResConfigSettings(models.TransientModel):  
    _inherit = 'res.config.settings'    

    smart_gateway = fields.Boolean(
        'Smart SMS Gateway',
        default=False,
        help="Activating this option will allow the user to use Smart SMS Gateway",
        readonly=False
    )
    smart_gateway_url = fields.Char('Smart API URL')
    smart_gateway_token = fields.Char('Smart API Token')

    @api.model
    def get_values(self):
      res = super(AWBResConfigSettings, self).get_values()
      params = self.env['ir.config_parameter'].sudo()
      smart_gateway = params.get_param('smart_gateway', default=False)
      smart_gateway_url = params.get_param('smart_gateway_url', default=False)
      smart_gateway_token = params.get_param('smart_gateway_token', default=False)
      res.update(
          smart_gateway=smart_gateway,
          smart_gateway_url=smart_gateway_url,
          smart_gateway_token=smart_gateway_token,
      )
      return res

    @api.model
    def set_values(self):
        super(AWBResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('smart_gateway', self.smart_gateway)
        params.set_param('smart_gateway_url', self.smart_gateway_url)
        params.set_param('smart_gateway_token', self.smart_gateway_token)

    @api.model
    def set_sms_admin_access(self):
      users = self.env['res.users'].search([])
      users_with_settings = users.filtered(lambda user: user.has_group("base.group_system"))
      _logger.info("User/s with settings permission, Assigning as Account Officer Central")
      _logger.info(users_with_settings.name_get())
      if users_with_settings:
        group = self.env.ref("awb_generic_sms.awb_sms_central")
        group.users = [(4, user.id) for user in users_with_settings]