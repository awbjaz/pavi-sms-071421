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
        try:
            if not self.sales_force:
                self.connect_to_salesforce()

            # Field/s removed due to errors found with usage with PAVI SalesForce: 
            #  ExpectedRevenue
            query = """
                    SELECT 
                        Id, name, AccountId, Amount, CloseDate,  Description, LastMOdifiedDate, 
                        HasOpenActivity, IsDeleted, IsWon, OwnerId, Probability, 
                        LastActivityDate, StageName, type, leadSource, CampaignId,
                        Preferred_Speed_Bandwidth__c,
                        Product_Sub_Type__c,
                        Product_Type__c,
                        Payment_OR_No__c,
                        Device_Fee__c,
                        Proof_of_Billing_Electricity_or_Water__c
                    FROM opportunity
                    WHERE StageName = 'Closed Won'
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

        except Exception as e:
            _logger.error(e, exc_info=True)
            raise osv.except_osv("Error Details!", e)

    def _create_lead_data(self, lead, lead_stage, campaign, medium, source):
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
            'sf_type': lead['Type'] if lead['Type'] else None
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

    def _find_and_link_opportunity_products(self, opportunity):
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
            """  % (opportunity['salesforce_id'])
        rows = self.sales_force.query(query)['records']

        # TODO: add code to process product entries

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
                        self._find_and_link_opportunity_products(lead_data)
                        self.env.cr.commit()
                    else:
                        lead_stage = self.env['crm.stage'].search([('name', '=', lead['StageName'])])
                        if not lead_stage:
                            lead_stage = self.env['crm.stage'].create({
                                'name': lead['StageName'],
                            })

                        lead_data = self._create_lead_data(lead, lead_stage, campaign, medium, source)
                        odoo_lead.write(lead_data)
                        self._find_and_link_opportunity_products(lead_data)
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
