# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    generated_num = fields.Char(string="Generated Number", stored=True, readonly=True, required=False, copy=False, default='')
    generated_num_plus_name = fields.Char(string="Description", stored=True, readonly=True, required=False, copy=False, default='')
 
    @api.model   
    def create(self, vals):
        vals['generated_num'] = self.env['ir.sequence'].next_by_code('hr.expense.generated.number.seq.code') 
        vals['generated_num_plus_name'] = (vals['generated_num'] or '') + '/' + (vals['name'] or '')
        result = super(HrExpense, self).create(vals)
        return result 

    def name_get(self):
        data = []
        for rec in self:
            display_value = f"{rec.generated_num}/{rec.name}"
            data.append((rec.id, display_value))
        return data

    @api.onchange('name')
    def _onchange_name(self):
        self.update({
            'generated_num_plus_name': f"{self.generated_num}/{self.name}"
        })



class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    generated_num = fields.Char(string="Generated Number", stored=True, readonly=True, required=False, copy=False, default='')
    generated_num_plus_name = fields.Char(string="Description", stored=True, readonly=True, required=False, copy=False, default='')
    
    @api.model   
    def create(self, vals):
        vals['generated_num'] = self.env['ir.sequence'].next_by_code('hr.expense.sheet.gen.number.seq.code')
        vals['generated_num_plus_name'] = (vals['generated_num'] or '') + '/' + (vals['name'] or '')
        result = super(HrExpenseSheet, self).create(vals)
        return result 

    def name_get(self):
        data = []
        for rec in self:
            display_value = f"{rec.generated_num}/{rec.name}"
            data.append((rec.id, display_value))
        return data

    @api.onchange('name')
    def _onchange_name(self):
        self.update({
            'generated_num_plus_name': f"{self.generated_num}/{self.name}"
        })
