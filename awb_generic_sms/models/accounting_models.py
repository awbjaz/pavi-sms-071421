from odoo import api, fields, models, exceptions, _


class InheritAccountMove(models.Model):
    _inherit = 'account.move'

    month = fields.Char(string="Invoice Month", readonly=True, default='April')
    msf_php = fields.Float(string="Monthly Service Fee", readonly=True, default='1300.00')
    arrears = fields.Float(string="Arrears", readonly=True, default="0.00")
    bill_num = fields.Char(string="Bill Number", readonly=True, default='155143')
    bill_covered = fields.Char(string="Bill Covered", readonly=True, default='04/01/2021 to 04/30/2021')
