from odoo import models, fields


class CustomLead(models.Model):
    _inherit = "crm.lead"

    sf_type = fields.Selection([("New", "New"),
                                ("Upgrade", "Upgrade"),
                                ("Recontract", "Recontract"),
                                ("Downgrade", "Downgrade"),
                                ("Reconnection", "Reconnection"),
                                ("Convert", "Convert"),
                                ("Disconnected", "Disconnected"),
                                ("Pre-Termination", "Pre-Termination"),
                                ], string='Type')
