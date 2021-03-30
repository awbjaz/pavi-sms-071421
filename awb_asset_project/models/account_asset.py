from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class AccountAsset(models.Model):
    _inherit = 'account.asset'
    _description = 'Asset/Revenue Recognition'
    
    project_id = fields.Many2one('project.project', string='Project')
    location_id = fields.Many2one('subscriber.location', string='Location')
    
    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            self.location_id = self.project_id.subscriber_location_id.id