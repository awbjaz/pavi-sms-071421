import logging
import datetime

from odoo import models, _
from openerp import _
from openerp.osv import osv

_logger = logging.getLogger(__name__)


class SalesForceImporterProducts(models.Model):
    _inherit = 'salesforce.connector'

    def creating_products(self, products):
        _logger.info(f'Creating Products {len(products)}')
        salesforce_ids = []
        for idx, product in enumerate(products):
            _logger.debug(f'Processing Products: {idx} out of {len(products)}')

            if not product['Family'] or not product.get('Type__c') or not product.get('Facility_Type__c'): 
                _logger.info(f'Products without Category: {product["Id"]}')
                continue

            domain = [('salesforce_id', '=', product['Id']),
                      ('active', 'in', (True, False))]
            odoo_product = self.env['product.template'].search(domain)
            all_category = self.env['product.category'].search([('name', '=', 'All')])
            if product['Family']:
                category_name = product['Family']
                category = self.env['product.category'].search([('name', '=', category_name), ('parent_id', '=', all_category.id)])
                if not category:
                    category = self.env['product.category'].create({
                        'name': category_name,
                        'parent_id': all_category.id
                    })
                    self.env.cr.commit()

            if product.get('Type__c'):
                category_name = product['Type__c']
                sub_category = self.env['product.category'].search([('name', '=', category_name), ('parent_id', '=', category.id)])
                if not sub_category:
                    category = self.env['product.category'].create({
                        'name': category_name,
                        'parent_id': category.id
                    })
                    self.env.cr.commit()
                else:
                    category = sub_category

            if product.get('Facility_Type__c'):
                category_name = product['Facility_Type__c']
                sub_category = self.env['product.category'].search([('name', '=', category_name)])
                if not sub_category:
                    category = self.env['product.category'].create({
                        'name': category_name,
                        'parent_id': category.id
                    })
                    self.env.cr.commit()
                else:
                    category = sub_category

            bandwidth = product.get('Bandwidth__c', '0')
            if bandwidth:
                bandwidth = bandwidth.lower().replace(' mbps', '')
            else:
                bandwidth = '0'

            data = {
                'salesforce_id': product['Id'],
                'name': product['Name'],
                'description': product['Description'],
                'list_price': product['Monthly_Subscription_Fee__c'] if product['Monthly_Subscription_Fee__c'] else None,
                'internet_usage': bandwidth,
                'default_code': product['ProductCode'],
                'last_modified': product['LastModifiedDate'],
                'categ_id': category.id,
                'device_fee': product.get('Device_Fee__c', 0),
                'type': 'service',
                'active': product.get('IsActive', True)
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
            salesforce_ids.append(product['Id'])

        _logger.info(f'Completed Creating Products {len(products)}')
        return salesforce_ids

    def import_products(self, Auto, id=None, fromOpportunity=False):
        _logger.info('----------------- STREAMTECH import_products')
        _logger.info(f'Import Products {Auto}')
        query = "SELECT Id, Name, ProductCode, Description" \
                ", Family, IsActive, Type__c, Facility_Type__c, Bandwidth__c" \
                ", Monthly_Subscription_Fee__c " \
                ", CreatedDate, LastModifiedDate " \
                " FROM Product2 " \
                " WHERE IsActive = True"

        if not self.sales_force:
            self.connect_to_salesforce()

        if id:
            query += " AND Id ='" + id + "'"
        elif not Auto and not fromOpportunity:
            if not self.from_date and self.to_date:
                raise osv.except_osv("Warning!", "Sorry; invalid operation, please select From Date")

            if self.from_date:
                query += " AND LastModifiedDate>=" + self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

            if self.to_date:
                to_date_query = " AND LastModifiedDate<=" + self.to_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                query += to_date_query
        elif Auto and not fromOpportunity:
            today = datetime.date.today()
            yesterday = today - datetime.timedelta(days=1)
            from_date_query = " AND LastModifiedDate>= " + yesterday.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
            to_date_query = " AND LastModifiedDate<=" + today.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
            query += from_date_query + to_date_query

        query += " LIMIT 5000"
        _logger.info(f'Query {query}')
        # products = self.sales_force.query(query)['records']
        products = self.sales_force.bulk.Product2.query(query)

        if not products and not fromOpportunity:
            raise osv.except_osv(_("Sync Details!"), _("No active product records found."))

        return self.creating_products(products)
