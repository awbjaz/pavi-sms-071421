# -*- coding: utf-8 -*-

import logging


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('default_code')
    def _check_unique_default_code(self):
        for product in self:
            if not product.default_code:
                continue

            domain = [('default_code', '=', product.default_code),
                      ('id', '!=', product.id)]
            products = self.env['product.template'].search(domain, limit=1)
            _logger.debug(f'Checking Products: {product.default_code} {products}')
            if len(products) > 0:
                raise ValidationError(f'Invalid reference code! Product Code is already used by {products.name}.')

            return True
