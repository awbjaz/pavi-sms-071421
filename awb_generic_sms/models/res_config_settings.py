# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AWBResConfigSettings(models.TransientModel):  
    _inherit = 'res.config.settings'    

    smart_gateway = fields.Boolean(
        'Smart SMS Gateway',
        default=False,
        help="Activating this option will allow the user to use Smart SMS Gateway",
        readonly=False
    )

    @api.model
    def get_values(self):
      res = super(AWBResConfigSettings, self).get_values()
      params = self.env['ir.config_parameter'].sudo()
      smart_gateway = params.get_param('smart_gateway', default=False)
      res.update(
          smart_gateway=smart_gateway,
      )
      return res

    @api.model
    def set_values(self):
        super(AWBResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'smart_gateway', self.smart_gateway)
