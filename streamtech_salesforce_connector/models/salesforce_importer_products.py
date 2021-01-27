import logging
import datetime

from odoo import models
from openerp.osv import osv

_logger = logging.getLogger(__name__)


class SalesForceImporterProducts(models.Model):
    _inherit = 'salesforce.connector'

    def creating_products(self, products):
        _logger.info(f'Creating Products {len(products)}')
        salesforce_ids = []
        for idx, product in enumerate(products):
            _logger.debug(f'Processing Products: {idx} out of {len(products)}')
            domain = [('salesforce_id', '=', product['Product2']['Id']),
                      ('active', 'in', (True, False))]
            odoo_product = self.env['product.template'].search(domain)
            category = self.env['product.category'].search([('name', '=', 'All')])
            if product['Product2']['Family']:
                category_name = product['Product2']['Family']
                category = self.env['product.category'].search([('name', '=', category_name)])
                if not category:
                    category = self.env['product.category'].create({
                        'name': category_name,
                        'parent_id': category.id
                    })
                    self.env.cr.commit()

            if product['Product2'].get('Type__c'):
                category_name = product['Product2']['Type__c']
                sub_category = self.env['product.category'].search([('name', '=', category_name)])
                if not sub_category:
                    category = self.env['product.category'].create({
                        'name': category_name,
                        'parent_id': category.id
                    })
                    self.env.cr.commit()
                else:
                    category = sub_category

            if product['Product2'].get('Facility_Type__c'):
                category_name = product['Product2']['Facility_Type__c']
                sub_category = self.env['product.category'].search([('name', '=', category_name)])
                if not sub_category:
                    category = self.env['product.category'].create({
                        'name': category_name,
                        'parent_id': category.id
                    })
                    self.env.cr.commit()
                else:
                    category = sub_category

            bandwidth = product['Product2'].get('Bandwidth__c', '0')
            if bandwidth:
                bandwidth = bandwidth.lower().replace(' mbps', '')
            else:
                bandwidth = '0'

            data = {
                'salesforce_id': product['Product2']['Id'],
                'name': product['Product2']['Name'],
                'description': product['Product2']['Description'],
                'list_price': product['UnitPrice'] if product['UnitPrice'] else None,
                'internet_usage': bandwidth,
                'default_code': product['Product2']['ProductCode'],
                'last_modified': product['LastModifiedDate'],
                'categ_id': category.id,
                'active': product['Product2'].get('IsActive', True)
            }

            if not odoo_product:
                data['location'] = 'SalesForce Product'
                new_product_template = self.env['product.template'].create(data)
                domain = [('product_tmpl_id', '=', new_product_template.id)]
                product_product = self.env['product.product'].search(domain)
                if not product_product:
                    self.env['product.product'].create({
                        'product_tmpl_id': new_product_template.id
                    })
                else:
                    product_product.write({
                        'product_tmpl_id': new_product_template.id
                    })
                self.env.cr.commit()
            elif odoo_product.last_modified != product['LastModifiedDate']:
                odoo_product.write(data)
                self.env.cr.commit()
            salesforce_ids.append(product['Product2']['Id'])

        return salesforce_ids

    def import_products(self, Auto):
        _logger.info(f'Import Products {Auto}')
        query = "SELECT Product2.Id, Product2.Name, Product2.ProductCode, Product2.Description" \
                ", Product2.Family, Product2.IsActive, Product2.Type__c, Product2.Facility_Type__c, Product2.Bandwidth__c" \
                ", UnitPrice " \
                ", Product2.CreatedDate, LastMOdifiedDate " \
                " from PriceBookEntry" \
                # " limit 10"
        _logger.info(f'Query {query}')
        try:
            if not self.sales_force:
                self.connect_to_salesforce()

            if not Auto:
                if not self.from_date and self.to_date:
                    raise osv.except_osv("Warning!", "Sorry; invalid operation, please select From Date")

                if self.from_date:
                    query += " where Product2.CreatedDate>=" + self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                if self.to_date:
                    to_date_query = " and Product2.CreatedDate<=" + self.to_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                    query += to_date_query
            else:
                today = datetime.date.today()
                yesterday = today - datetime.timedelta(days=1)
                from_date_query = " where Product2.CreatedDate>= " + yesterday.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                to_date_query = " and Product2.CreatedDate<=" + today.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                query += from_date_query + to_date_query

            products = self.sales_force.bulk.PriceBookEntry.query(query)
            return self.creating_products(products)

        except Exception as e:
            raise osv.except_osv("Error Details!", e)
