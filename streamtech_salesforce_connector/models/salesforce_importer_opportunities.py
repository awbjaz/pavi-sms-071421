import logging
import datetime
import unicodedata
from dateutil.relativedelta import relativedelta

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
        account_query = """
                    Account.Id, Account.IsPersonAccount,
                    Account.Name, Account.FirstName, Account.MiddleName, Account.LastName,
                    Account.Gender__c, Account.Birth_Date__c, Account.Civil_Status__c,
                    Account.Home_Ownership__c,
                    Account.Account_Classification__c, Account.Account_Sub_Classification__c,
                    Account.Customer_Type__c,
                    Account.Type, Account.Zone_Type_Acc__c, Account.Zone_Sub_Type_Acc__c,

                    Account.PersonMobilePhone, Account.Mobile_Phone__c,
                    Account.Person_Secondary_Mobile_Number__c, Account.Secondary_Mobile_Number__pc,
                    Account.Phone, Account.Person_Secondary_Phone__c, Account.PersonOtherPhone,

                    Account.Area_Code_BillingAddress__c,
                    Account.Barangay_BillingAddress__c,
                    Account.NameBldg_NoFloor_No_BillingAddress__c,
                    Account.Street_BillingAddress__c,
                    Account.City_BillingAddress__c,
                    Account.Province_BillingAddress__c,
                    Account.Region_BillingAddress__c,

                    Account.Area_Code_BusinessAddress__c,
                    Account.Barangay_BusinessAddress__c,
                    Account.NameBldg_NoFloor_No_BusinessAddress__c,
                    Account.Street_BusinessAddress__c,
                    Account.City_BusinessAddress__c,
                    Account.Province_BusinessAddress__c,
                    Account.Region_BusinessAddress__c,

                    Account.House_No_BL_Phase__c,
                    Account.Barangay_Subdivision_Name__c,
                    Account.City__c,
                    Account.Province__c,
                    Account.Region__c,
                    Account.Person_Contact_Name__c,

                    Account.PersonEmail,
                    Account.Person_Secondary_Email_Address__c,
                    Account.Secondary_Email_Address__pc
                """
        query = f"""
                SELECT
                    Id, Opportunity_Number__c, name, AccountId, Amount, CloseDate,  Description, LastMOdifiedDate,
                    HasOpenActivity, IsDeleted, IsWon, OwnerId, Probability,
                    LastActivityDate, StageName, Type, leadSource, CampaignId,
                    Old_Customer_Number__c,
                    Preferred_Speed_Bandwidth__c,
                    Product_Type__c,
                    Product_Sub_Type__c,
                    Payment_OR_No__c,
                    Device_Fee__c,
                    Valid_ID__c,
                    Valid_ID_of_Homeowner__c,
                    Proof_of_Billing_Electricity_or_Water__c,
                    Total_Discount_AMount__c,
                    Sum_of_Installation_Cost__c,
                    Contract_Term__c,
                    Sub_Stages__c,
                    Initial_Payment_Date__c,
                    Area_ODOO__c,
                    Business_Unit_Groups__c,
                    (SELECT SLA_Activation_Actual_End_Date__c FROM opportunity.Job_Orders__r),
                    (SELECT
                        PricebookEntryId, Product2Id, ProductCode,
                        Name, Device_Fee__c, Quantity,
                        Total_Cash_Out__c, UnitPrice
                    FROM
                        opportunity.OpportunityLineItems),
                    {account_query}
                FROM opportunity
                WHERE  CreatedDate >= 2021-03-15T00:00:00+0000
                AND ((StageName = 'Closed Won' AND Sub_Stages__c in ('Completed Activation'))
                OR StageName = 'Closed Lost')
                AND Opportunity_In_Effect__c = true
                """

        if not Auto:
            if not self.from_date and not self.to_date:
                pass

            elif not self.from_date and self.to_date:
                raise osv.except_osv("Warning!", "Sorry; invalid operation, please select From Date")

            elif self.from_date and not self.to_date:
                from_date_query = " AND LastModifiedDate>= " + self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                query = query + from_date_query

            elif self.from_date and self.to_date:
                from_date_query = " AND LastModifiedDate>= " + self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                to_date_query = " AND LastModifiedDate<=" + self.to_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                query = query + from_date_query + to_date_query

        else:
            today = datetime.date.today()
            yesterday = today - datetime.timedelta(days=1)
            from_date_query = " AND LastModifiedDate>=" + yesterday.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
            to_date_query = " AND LastModifiedDate<=" + today.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

            query = query + from_date_query + to_date_query

        query += " LIMIT 1000 "
        opportunities = self.sales_force.bulk.Opportunity.query(query)
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

        cable = lead.get('Product_Sub_Type__c', '')
        if cable:
            cable = cable.lower()
        else:
            cable = ''

        if 'digital' in cable.lower():
            cable = 'digital'
        elif 'analog' in cable:
            cable = 'analog'
        else:
            cable = 'none'

        promo = lead.get('Total_Discount_AMount__c', 0)
        if promo and promo > 0:
            promo = True
        else:
            promo = False

        has_id = lead.get('Valid_ID__c', False) or lead['Valid_ID_of_Homeowner__c']

        speed = lead.get('Preferred_Speed_Bandwidth__c', '0')
        if speed:
            speed = int(speed)
        else:
            speed = 0

        zone = self._find_zone(lead['Area_ODOO__c'])

        contract_term = lead.get('Contract_Term__c', 0)
        if contract_term:
            contract_term = int(contract_term)

        # Business Unit
        sf_sales_team = lead.get('Business_Unit_Groups__c', None)
        sales_team_id = None
        if sf_sales_team:
            # Find corresponding entry in Odoo CRMr team records
            sales_team_result = self._find_sales_team()
            if (len(sales_team_result) > 0):
                sales_team_id = sales_team_result[0].id

        job_orders = lead.get('Job_Orders__r', {})
        contract_start_date = None
        contract_end_date = None
        if job_orders:
            for jo in job_orders.get('records', []):
                contract_start_date = jo.get('SLA_Activation_Actual_End_Date__c', None)
                if contract_start_date and contract_term:
                    if isinstance(contract_start_date, int):
                        contract_start_date = datetime.datetime.fromtimestamp(contract_start_date/1000)
                    else:
                        contract_start_date = datetime.datetime.strptime(contract_start_date, "%Y-%m-%dT%H:%M:%S.000+0000")

                    contract_end_date = contract_start_date + relativedelta(months=contract_term)

                    contract_start_date = contract_start_date.strftime("%Y-%m-%dT%H:%M:%S")
                    contract_end_date = contract_end_date.strftime("%Y-%m-%dT%H:%M:%S")

        lead = {
            'salesforce_id': lead['Id'],
            'name': lead['Name'],
            'opportunity_number': lead['Opportunity_Number__c'],
            'account_identification': lead.get('Old_Customer_Number__c'),
            'planned_revenue': lead['Amount'] if lead['Amount'] else None,
            'probability': lead['Probability'] if lead['Probability'] else 0,
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
            'contract_term': contract_term,
            # 'no_tv': ,
            # 'plan': # Mapping
            'internet_speed': speed,
            # 'device': '', # Mapping
            'cable': cable,
            'promo': promo,
            'has_id': has_id,
            'has_proof_bill': lead.get('Proof_of_Billing_Electricity_or_Water__c', False),
            'has_lease_contract': '',
            'others': lead.get('Description'),
            'initial_payment': lead.get('Sum_of_Installation_Cost__c', 0.0),
            'or_number': lead.get('Payment_OR_No__c', ''),
            'payment_date': lead.get('Initial_Payment_Date__c'),
            'billing_type': 'physical',
            'job_order_status': substage,
            'subscription_status': subscription_status,
            'zone': zone.id,
            'company_id': zone.company_id.id,
            'team_id': sales_team_id
        }

        if contract_start_date and contract_end_date:
            lead['contract_start_date'] = contract_start_date
            lead['contract_end_date'] = contract_end_date

        # Adjust typo from PAVI SF data so it will be spelled right upon Odoo import
        if lead['sf_type'] == 'Reconnect ion':
            lead['sf_type'] = 'Reconnection'

        return lead

    def _create_lead_product_data(self, opportunity, products):
        items = []
        _logger.debug(f'Adding Products {len(products)}')
        device_fee = 0
        for product in products:
            domain = [('salesforce_id', '=', product['Product2Id']),
                      ('active', 'in', (True, False))]
            odoo_product = self.env['product.template'].search(domain)
            if not odoo_product:
                _logger.debug(f'Import Product: {product}')
                self.import_products(False, product['Product2Id'])
                odoo_product = self.env['product.template'].search([('salesforce_id', '=', product['Product2Id'])])

            total_cash_out = product['Total_Cash_Out__c']
            if product['Device_Fee__c'] and product['Device_Fee__c'] > 0:
                device_fee += product['Device_Fee__c']
                total_cash_out -= product['Device_Fee__c']

            data = {
                'product_id': odoo_product.id,
                'quantity': product['Quantity'],
                'unit_price': product['UnitPrice'],
                'total_price': total_cash_out,
                'device_fee': 0
            }
            items.append((0, 0, data))

        if device_fee > 0:
            data = {
                'product_id': self.env.ref('awb_subscriber_product_information.product_device_fee').id,
                'quantity': 1,
                'unit_price': device_fee,
                'total_price': device_fee,
                'device_fee': 0
            }
            items.append((0, 0, data))

        opportunity.update({'product_lines': [(5, 0, 0)]})
        _logger.debug(f'Adding Items {len(items)}')
        if len(items):
            opportunity.update({'product_lines': items})

    def _get_partner_data(self, lead):
        lead_partner = self.env['res.partner'].search([('salesforce_id', '=', lead['AccountId'])])
        partner = lead['Account']
        zone = self._find_zone(lead['Area_ODOO__c'])
        lead_partner = self._create_customer(partner, lead_partner, zone)

        return lead_partner

    def _find_sales_team(self, sales_team):
        team = self.env['crm.team'].search([('name', '=ilike', sales_team)], limit=1)
        return team

    def _find_zone(self, zone):
        zone = self.env['subscriber.location'].search([('name', '=', zone)], limit=1)
        return zone

    def creating_opportunities(self, opportunities):
        salesforce_ids = []
        campaign = None
        medium = None
        source = None

        completed_stage = self.env.ref('awb_subscriber_product_information.stage_completed')

        for idx, lead in enumerate(opportunities):
            _logger.info(f'----------------- STREAMTECH creating_opportunities Lead[{lead["Opportunity_Number__c"]}]: {idx} of {len(opportunities)}')
            products = lead['OpportunityLineItems']
            if products:
                products = products['records']
            else:
                products = []

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

                lead_stage = self.env['crm.stage'].search([('name', '=', lead['StageName'])])
                if not lead_stage:
                    lead_stage = self.env['crm.stage'].create({
                        'name': lead['StageName'],
                    })

                if odoo_lead.stage_id.id == completed_stage.id:
                    lead_stage = completed_stage

                lead_data = self._create_lead_data(lead, lead_stage, campaign, medium, source)
                if lead['AccountId']:
                    lead_partner = self._get_partner_data(lead)
                    lead_data['partner_id'] = lead_partner.id
                    _logger.debug(f'Subscriber Location {lead_partner.subscriber_location_id}')
                    if lead_partner.subscriber_location_id:
                        lead_data['zone'] = lead_partner.subscriber_location_id.id

                _logger.debug(f'Create Product')
                self._create_lead_product_data(odoo_lead, products)
                _logger.debug(f'Created Product')
                # _logger.debug(f'Updating data: {odoo_lead.id}: {lead_data}')
                # try:
                odoo_lead.write(lead_data)
                self.env.cr.commit()
                # except Exception as e:
                #     _logger.debug(f'Error: {e}')
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
                lead_stage = self.env['crm.stage'].search([('name', '=', lead['StageName'])])
                if not lead_stage:
                    lead_stage = self.env['crm.stage'].create({
                        'name': lead['StageName'],
                    })

                lead_data = self._create_lead_data(lead, lead_stage, campaign, medium, source)
                lead_data['location'] = 'SalesForce'

                if lead['AccountId']:
                    lead_partner = self._get_partner_data(lead)
                    lead_data['partner_id'] = lead_partner.id

                # try:
                odoo_lead = self.env['crm.lead'].create(lead_data)
                _logger.debug(f'Create Product')
                self._create_lead_product_data(odoo_lead, products)
                _logger.debug(f'Created Product')
                _logger.debug(f'Creating data: {lead_data}')
                self.env.cr.commit()
                # except Exception as e:
                #     _logger.debug(f'Error: {e}')

            _logger.info(f'STREAMTECH creating_opportunities Lead: {idx} of {len(opportunities)} ----------------- ')
            salesforce_ids.append(lead['Id'])

        return salesforce_ids
