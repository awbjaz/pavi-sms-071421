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
                    (SELECT SLA_Activation_Actual_End_Date__c FROM opportunity.Job_Orders__r),
                    (SELECT
                        PricebookEntryId, Product2Id, ProductCode,
                        Name, Device_Fee__c, Quantity,
                        Total_Cash_Out__c, UnitPrice
                    FROM
                        opportunity.OpportunityLineItems),
                    {account_query}
                FROM opportunity
                WHERE ((StageName = 'Closed Won' AND Sub_Stages__c in ('Completed Activation'))
                OR StageName = 'Closed Lost')
                AND Opportunity_In_Effect__c = true
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

        contract_term = lead.get('Contract_Term__c', 0)
        if contract_term:
            contract_term = int(contract_term)

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
            'subscription_status': subscription_status
        }

        if contract_start_date and contract_end_date:
            lead['contract_start_date'] = contract_start_date
            lead['contract_end_date'] = contract_end_date

        # Adjust typo from PAVI SF data so it will be spelled right upon Odoo import
        if lead['sf_type'] == 'Reconnect ion':
            lead['sf_type'] = 'Reconnection'

        return lead

    def _create_lead_partner_data(self, partner, lead_partner):
        data = {
            'salesforce_id': partner['Id'],
            'name': partner['Name'],
            'account_type': '',
            'outside_sourced': True,
            'location': 'SalesForce Opportunity Account',
            'customer_rank': 1,
            'last_name': '',
            'first_name': '',
            'middle_name': '',
            'birthday': False,
            'gender': '',
            'subscriber_type': '',
            'account_classification': '',
            'account_subclassification': None,
            'type': '',
        }

        type_data = partner['Type']
        if type_data:
            data['type'] = type_data

        if partner.get('IsPersonAccount'):
            data['is_company'] = False
            gender = partner['Gender__c']
            if gender:
                gender = gender.lower()
            else:
                gender = None

            civil_status = partner.get('Civil_Status__c')
            if civil_status:
                civil_status = civil_status.lower()
                data['civil_status'] = civil_status

            home_ownership = partner['Home_Ownership__c']
            if home_ownership:
                home_ownership = home_ownership.lower()
                home_ownership = home_ownership.replace('\xa0', ' ')
                if home_ownership == 'living with relatives':
                    home_ownership = 'living_relatives'
                elif home_ownership == 'company provided':
                    home_ownership = 'company_provided'
                data['home_ownership'] = home_ownership

            account_group = partner['Zone_Type_Acc__c']
            if account_group:
                account_group = account_group.lower()
                data['account_group'] = account_group
                data['zone_type'] = account_group

            zone_subtype = partner['Zone_Sub_Type_Acc__c']
            if zone_subtype:
                zone_sub = self.env['zone.subtype'].search([('name', '=', zone_subtype)])
                if not zone_sub:
                    zone_sub = self.env['zone.subtype'].create({'name': zone_subtype, 'zone_type': account_group})

                data['zone_subtype'] = zone_sub.id

            email = partner['PersonEmail']
            if email:
                data['email'] = email

            mobile = partner['PersonMobilePhone']
            phone = partner['PersonOtherPhone']

            birthday = partner['Birth_Date__c']
            if birthday:
                data['birthday'] = birthday

            data.update({
                'first_name': partner['FirstName'],
                'middle_name': partner['MiddleName'],
                'last_name': partner['LastName'],
                'mobile': mobile,
                'phone': phone,
                'gender': gender
                })

            street1 = partner['House_No_BL_Phase__c']
            street2 = partner['Barangay_Subdivision_Name__c']

            province_name = partner['Province__c']
            city_name = partner['City__c']
        else:
            data['is_company'] = True
            subscriber_type = partner.get('Customer_Type__c')
            if subscriber_type:
                subscriber_type = subscriber_type.lower()
                data['subscriber_type'] = subscriber_type

            classification = partner['Account_Classification__c']
            if classification:
                classification = classification.lower()
                if classification == 'affiliate/internal':
                    classification = 'internal'
                data['account_classification'] = classification

            sub_classification = partner.get('Account_Sub_Classification__c')
            if sub_classification:
                sub_class = self.env['partner.classification'].search([('name', '=', sub_classification)])
                if not sub_class:
                    sub_class = self.env['partner.classification'].create({'name': sub_classification, 'account_classification': classification})

                data['account_subclassification'] = sub_class.id

            bldg_billing = partner.get('NameBldg_NoFloor_No_BillingAddress__c')
            street_billing = partner.get('Street_BillingAddress__c')
            brgy_billing = partner.get('Barangay_BillingAddress__c')

            province_name = partner.get('Province_BillingAddress__c')
            city_name = partner.get('City_BillingAddress__c')

            mobile = partner['Mobile_Phone__c']
            phone = partner['Phone']

            data['mobile'] = mobile
            data['phone'] = phone

            street1 = f'{bldg_billing} {street_billing}'
            street2 = brgy_billing

        province_id = False
        if province_name:
            province_name = province_name.replace('\xa0', ' ')
            if province_name == 'Compostela Valley':
                province_name = 'Davao de Oro'
            elif province_name == 'Western Samar':
                province_name = 'Samar'
            province_id = self.env['res.country.state'].search([('name', '=ilike', province_name)])

        city_id = False
        if city_name:
            city_name = city_name.replace('\xa0', ' ')
            city_name = city_name.replace(' (Rizal)', '')
            city_name = city_name.replace(' (Albor)', '')
            city_name = city_name.replace('Bumbaran', 'Amai Manabilang')
            city_name = city_name.replace('General Salipada K. Pendatun', 'Gen. S.K. Pendatun')
            city_name = city_name.replace('Sultan Sumagka', 'Talitay')
            city_name = city_name.replace('Datu Montawal', 'Pagagawan')
            city_name = city_name.replace('Senator Ninoy Aquino', 'Sen. Ninoy Aquino')
            city_name = city_name.replace('President Manuel A. Roxas', 'Pres. Manuel A. Roxas')
            city_id = self.env['res.city'].search([('name', '=ilike', city_name), ('state_id', '=?', province_id.id)])

        if not city_id or len(city_id) > 1:
            _logger.error(f'Multiple Cities: {data["salesforce_id"]} {city_name}:{city_id} {province_name}:{province_id}')

        data.update({
            'street': street1,
            'street2': street2,
            'city_id': city_id.id if city_id else False,
            'state_id': province_id.id if province_id else False,
            'region_id': province_id.region_id.id if province_id and province_id.region_id else False,
            'country_id': province_id.country_id.id if province_id and province_id.country_id else False
            })

        if lead_partner:
            lead_partner.write(data)
        else:
            lead_partner = self.env['res.partner'].create(data)

        return lead_partner

    def _create_lead_product_data(self, opportunity, products):
        items = []
        _logger.debug(f'Adding Products {len(products)}')
        for product in products:
            domain = [('salesforce_id', '=', product['Product2Id']),
                      ('active', 'in', (True, False))]
            odoo_product = self.env['product.template'].search(domain)
            if not odoo_product:
                _logger.debug(f'Import Product: {product}')
                self.import_products(False, product['Product2Id'])
                odoo_product = self.env['product.template'].search([('salesforce_id', '=', product['Product2Id'])])

            data = {
                'product_id': odoo_product.id,
                'quantity': product['Quantity'],
                'unit_price': product['UnitPrice'],
                'total_price': product['Total_Cash_Out__c'],
                'device_fee': product['Device_Fee__c']
            }
            items.append((0, 0, data))

        opportunity.update({'product_lines': [(5, 0, 0)]})
        _logger.debug(f'Adding Items {len(items)}')
        if len(items):
            opportunity.update({'product_lines': items})

    def _get_partner_data(self, lead):
        lead_partner = self.env['res.partner'].search([('salesforce_id', '=', lead['AccountId'])])
        partner = lead['Account']
        lead_partner = self._create_lead_partner_data(partner, lead_partner)

        return lead_partner

    def creating_opportunities(self, opportunities):
        salesforce_ids = []
        campaign = None
        medium = None
        source = None

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

                lead_data = self._create_lead_data(lead, lead_stage, campaign, medium, source)
                if lead['AccountId']:
                    lead_partner = self._get_partner_data(lead)
                    lead_data['partner_id'] = lead_partner.id

                _logger.debug(f'Create Product')
                self._create_lead_product_data(odoo_lead, products)
                _logger.debug(f'Created Product')
                _logger.debug(f'Updating data: {odoo_lead.id}: {lead_data}')
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
                self.env['crm.lead'].create(lead_data)
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
