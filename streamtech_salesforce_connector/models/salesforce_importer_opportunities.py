import logging
import datetime
from pprint import pformat

from odoo import models, fields
from openerp.osv import osv

_logger = logging.getLogger(__name__)


class SalesForceImporterOpportunities(models.Model):
    _inherit = 'salesforce.connector'

    def import_opportunities(self, Auto):
        _logger.info('----------------- STREAMTECH import_opportunities')
        if not self.sales_force:
            self.connect_to_salesforce()

        # Field/s removed due to errors found with usage with PAVI SalesForce: 
        #  ExpectedRevenue
        query = """
                SELECT 
                    Id, name, AccountId, Amount, CloseDate,  Description, LastMOdifiedDate, 
                    HasOpenActivity, IsDeleted, IsWon, OwnerId, Probability, 
                    LastActivityDate, StageName, Type, leadSource, CampaignId,
                    Preferred_Speed_Bandwidth__c,
                    Product_Sub_Type__c,
                    Product_Type__c,
                    Payment_OR_No__c,
                    Device_Fee__c,
                    Valid_ID__c,
                    Proof_of_Billing_Electricity_or_Water__c,
                    Sum_of_Installation_Cost__c,
                    Contract_Term__c,
                    Sub_Stages__c
                FROM opportunity
                WHERE (StageName = 'Closed Won' AND Sub_Stages__c in ('Completed Activation'))
                OR StageName = 'Closed Lost'
                """

        if not Auto:
            if not self.from_date and not self.to_date:
                pass

            elif not self.from_date and self.to_date:
                raise osv.except_osv("Warning!", "Sorry; invalid operation, please select From Date")

            elif self.from_date and not self.to_date:
                from_date_query = " AND CreatedDate>= " + self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                query = query + from_date_query 

            elif self.from_date and self.to_date:
                from_date_query = " AND CreatedDate>= " + self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                to_date_query = " AND createdDate<=" + self.to_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                query = query + from_date_query + to_date_query

        else:
            today = datetime.date.today()
            yesterday = today - datetime.timedelta(days=1)
            from_date_query = " AND CreatedDate>=" + yesterday.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
            to_date_query = " AND createdDate<=" + today.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

            query = query + from_date_query + to_date_query

        _logger.debug(f'Query: {query}')
        opportunities = self.sales_force.query(query)['records']
        return self.creating_opportunities(opportunities)

        # except Exception as e:
        #     _logger.error(e, exc_info=True)
        #     raise osv.except_osv("Error Details!", e)

    def _create_lead_data(self, lead, lead_stage, campaign, medium, source):
        substage = lead.get('Sub_Stages__c', '')
        if substage == '':
            substage = 'new'
        elif substage == 'Pending Installation':
            substage = 'installation'
        elif substage == 'Completed Installation':
            substage = 'activation'
        elif substage == 'Completed Activation':
            substage = 'completed'
        elif substage == 'JO Cancelled':
            substage = 'cancel'
        else:
            substage = ''

        subscription_status = lead.get('Type', '')
        if subscription_status == 'New':
            subscription_status = 'new'
        elif subscription_status == 'Upgrade':
            subscription_status = 'upgrade'
        elif subscription_status == 'Recontract':
            subscription_status = 're-contract'
        elif subscription_status == 'Downgrade':
            subscription_status = 'downgrade'
        elif subscription_status == 'Reconnect ion':
            subscription_status = 'reconnection'
        elif subscription_status == 'Convert':
            subscription_status = 'convert'
        elif subscription_status == 'Disconnected':
            subscription_status = 'disconnection'
        elif subscription_status == 'Pre-Termination':
            subscription_status = 'pre-termination'
        else:
            subscription_status = ''

        speed = lead.get('Preferred_Speed_Bandwidth__c', '0')
        if speed:
            speed = int(speed)
        else:
            speed = 0

        lead = {
            'salesforce_id': lead['Id'],
            'name': lead['Name'],
            'planned_revenue': lead['Amount'] if lead['Amount'] else None,
            'probability': lead['Probability'] if lead['Probability'] else None,
            'type': 'opportunity',
            'date_closed': lead['CloseDate'] if lead['CloseDate'] else None,
            'stage_id': lead_stage.id,
            'campaign_id': campaign.id if campaign else None,
            'medium_id': medium.id if medium else None,
            'source_id': source.id if source else None,
            'description': lead['Description'] if lead['Description'] else None,
            'sf_type': lead['Type'] if lead['Type'] else None,
            'is_auto_quotation': True,
            'outside_source': True,
            # 'contract_start_date': '',
            # 'contract_end_date': '',
            'contract_term': lead.get('Contract_Term__c', 0),
            # 'no_tv': ,
            # 'plan': # Mapping
            'internet_speed': speed,
            # 'device': '', # Mapping
            # 'cable': '',
            # 'promo': '',
            'has_id': lead.get('Valid_ID__c', False),
            'has_proof_bill': lead.get('Proof_of_Billing_Electricity_or_Water__c', False),
            # 'has_lease_contract': '',
            # 'others': '',
            'initial_payment': lead.get('Sum_of_Installation_Cost__c', 0.0),
            'or_number': lead.get('Payment_OR_No__c', ''),
            # 'payment_date': '',
            # 'billing_type': '',
            'job_order_status': substage,
            'subscription_status': subscription_status,
        }

        # Adjust typo from PAVI SF data so it will be spelled right upon Odoo import
        if lead['sf_type'] == 'Reconnect ion':
            lead['sf_type'] = 'Reconnection'

        return lead

    def _create_lead_partner_data(self, partner):
        lead_partner = self.env['res.partner'].create({
            'salesforce_id': partner['Id'],
            'name': partner['Name'],
            'location': 'SalesForce Opportunity Account',
            'city': partner['ShippingCity'] if partner['ShippingCity'] else None,
            'street': partner['ShippingStreet'] if partner['ShippingStreet'] else None,
            'country_id': self.env['res.country'].search(
                [('name', '=', partner['ShippingCountry'])]).id if
            partner['ShippingCountry'] else None,
            'zip': partner['ShippingPostalCode'] if partner['ShippingPostalCode'] else None,
            'phone': partner['Phone'] if partner['Phone'] else None,
            'is_company': True,
            'customer_rank': 1,
        })
        return lead_partner

    def _create_lead_product_data(self, opportunity, products):
        items = []
        for product in products:
            odoo_product = self.env['product.template'].search([('salesforce_id', '=', product['Product2Id'])])
            data = {
                'product_id': odoo_product.id,
                'quantity': product['Quantity'],
                'unit_price': product['UnitPrice'],
                'total_price': product['TotalPrice']
            }
            items.append((0, 0, data))

        opportunity.update({'product_lines': [(5, 0, 0)]})
        opportunity.update({'product_lines': items})

    def _find_and_link_opportunity_products(self, opportunity, op_data):
        _logger.info('----------------- STREAMTECH _find_and_link_opportunity_products(')
        query = """
            SELECT
                oli.OpportunityId,
                oli.PricebookEntryId,
                oli.Product2Id,
                oli.ProductCode,
                oli.Name,
                oli.Quantity,
                oli.TotalPrice,
                oli.UnitPrice
            FROM
                OpportunityLineItem AS oli
            WHERE
                oli.OpportunityId = '%s'
            """ % (op_data['salesforce_id'])
        rows = self.sales_force.query(query)['records']

        # TODO: add code to process product entries
        _logger.debug(f'Products: {rows}')
        self._create_lead_product_data(opportunity, rows)

    def _process_opportunity_job_orders(self, opportunity):
        _logger.info('----------------- STREAMTECH _process_opportunity_job_orders(')
        query = """
            SELECT 
                jo.Id,
                jo.Name,
                jo.Job_Order_Number__c,
                jo.JO_Status__c,
                jo.Opportunity_Name__c
            FROM 
                Job_Order__c AS jo
            WHERE
                jo.Opportunity_Name__c = '%s'
            """  % (opportunity['salesforce_id'])
        rows = self.sales_force.query(query)['records']
        
        # TODO: add code to process job order entries

    def creating_opportunities(self, opportunities):
        _logger.info('----------------- STREAMTECH creating_opportunities')
        _logger.info(pformat(opportunities))

        try:
            salesforce_ids = []
            campaign = None
            medium = None
            source = None

            for lead in opportunities:
                odoo_lead = self.env['crm.lead'].search([('salesforce_id', '=', lead['Id'])])
                if odoo_lead:
                    if lead['CampaignId']:
                        campaign = self.env['utm.campaign'].search([('salesforce_id', '=', lead['CampaignId'])])
                        if not campaign:
                            query = "select id,name,type,status,StartDate,EndDate from campaign " \
                                    "where id='%s'" % str(lead['CampaignId'])
                            sf_campaign = self.sales_force.query(query)['records'][0]
                            campaign = self.env['utm.campaign'].create({
                                'salesforce_id': sf_campaign['Id'],
                                'name': sf_campaign['Name'],
                            })
                            medium = self.env['utm.campaign'].search([('name', '=', sf_campaign['Type'])])
                            if not medium:
                                medium = self.env['utm.medium'].create({
                                    'name': sf_campaign['Name'],
                                })
                            self.env.cr.commit()
                    if lead['LeadSource']:
                        source = self.env['utm.source'].search([('name', '=', lead['LeadSource'])])
                        if not source:
                            source = self.env['utm.source'].create({
                                'name': lead['LeadSource'],
                            })
                            self.env.cr.commit()

                    if lead['AccountId']:
                        lead_partner = self.env['res.partner'].search([('salesforce_id', '=', lead['AccountId'])])
                        if not lead_partner:
                            # Field/s removed due to errors found with usage with PAVI SalesForce: 
                            #  fax
                            query = "select id, name, shippingStreet," \
                                    "ShippingCity,Website, " \
                                    "ShippingPostalCode, shippingCountry, " \
                                    "phone, Description from account"

                            extend_query = " where id='" + lead['AccountId'] + "'"
                            partner = self.sales_force.query(query + extend_query)["records"][0]
                            lead_partner = self._create_lead_partner_data(partner)

                        lead_stage = self.env['crm.stage'].search([('name', '=', lead['StageName'])])
                        if not lead_stage:
                            lead_stage = self.env['crm.stage'].create({
                                'name': lead['StageName'],
                            })

                        lead_data = self._create_lead_data(lead, lead_stage, campaign, medium, source)
                        lead_data['partner_id'] = lead_partner.id
                        odoo_lead.write(lead_data)
                        self._find_and_link_opportunity_products(odoo_lead, lead_data)
                        self.env.cr.commit()
                    else:
                        lead_stage = self.env['crm.stage'].search([('name', '=', lead['StageName'])])
                        if not lead_stage:
                            lead_stage = self.env['crm.stage'].create({
                                'name': lead['StageName'],
                            })

                        lead_data = self._create_lead_data(lead, lead_stage, campaign, medium, source)
                        odoo_lead.write(lead_data)
                        self._find_and_link_opportunity_products(odoo_lead, lead_data)
                        self.env.cr.commit()
                else:
                    if lead['CampaignId']:
                        campaign = self.env['utm.campaign'].search([('salesforce_id', '=', lead['CampaignId'])])
                        if not campaign:
                            query = "select id,name,type,status,StartDate,EndDate from campaign " \
                                    "where id='%s'" % str(lead['CampaignId'])
                            sf_campaign = self.sales_force.query(query)['records'][0]
                            campaign = self.env['utm.campaign'].create({
                                'salesforce_id': sf_campaign['Id'],
                                'name': sf_campaign['Name'],
                            })
                            medium = self.env['utm.campaign'].search([('name', '=', sf_campaign['Type'])])
                            if not medium:
                                medium = self.env['utm.medium'].create({
                                    'name': sf_campaign['Name'],
                                })
                            self.env.cr.commit()
                    if lead['LeadSource']:
                        source = self.env['utm.source'].search([('name', '=', lead['LeadSource'])])
                        if not source:
                            source = self.env['utm.source'].create({
                                'name': lead['LeadSource'],
                            })
                            self.env.cr.commit()

                    if lead['AccountId']:
                        lead_partner = self.env['res.partner'].search([('salesforce_id', '=', lead['AccountId'])])
                        if not lead_partner:
                            # Field/s removed due to errors found with usage with PAVI SalesForce: 
                            #  fax
                            query = "select id, name, shippingStreet," \
                                    "ShippingCity,Website, " \
                                    "ShippingPostalCode, shippingCountry, " \
                                    "phone, Description from account"

                            extend_query = " where id='" + lead['AccountId'] + "'"
                            partner = self.sales_force.query(query + extend_query)["records"][0]
                            lead_partner = self._create_lead_partner_data(partner)

                        lead_stage = self.env['crm.stage'].search([('name', '=', lead['StageName'])])
                        if not lead_stage:
                            lead_stage = self.env['crm.stage'].create({
                                'name': lead['StageName'],
                            })

                        lead_data = self._create_lead_data(lead, lead_stage, campaign, medium, source)
                        lead_data['location'] = 'SalesForce'
                        lead_data['partner_id'] = lead_partner.id
                        self.env['crm.lead'].create(lead_data)
                        self._find_and_link_opportunity_products(lead_data)
                        self.env.cr.commit()
                    else:
                        lead_stage = self.env['crm.stage'].search([('name', '=', lead['StageName'])])
                        if not lead_stage:
                            lead_stage = self.env['crm.stage'].create({
                                'name': lead['StageName'],
                            })

                        lead_data = self._create_lead_data(lead, lead_stage, campaign, medium, source)
                        lead_data['location'] = 'SalesForce'
                        self.env['crm.lead'].create(lead_data)
                        self._find_and_link_opportunity_products(lead_data)
                        self.env.cr.commit()
                salesforce_ids.append(lead['Id'])

            # TODO; uncomment
            return salesforce_ids
            # TODO; remove
            # return []

        except Exception as e:
            raise osv.except_osv("Error Details!", e)
