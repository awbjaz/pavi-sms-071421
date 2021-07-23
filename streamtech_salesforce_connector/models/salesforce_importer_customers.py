from ..helpers.salesforce_connector import SalesForceConnect
import logging
import datetime

from odoo import models
from openerp.osv import osv

_logger = logging.getLogger(__name__)


class SalesForceImporterCustomers(models.Model):
    _inherit = 'salesforce.connector'

    def import_customers(self, Auto):
        _logger.info('----------------- STREAMTECH import_customers')

        connector = SalesForceConnect()
        self.sales_force = connector.connect_salesforce(model=self)

        # Field/s removed due to errors found with usage with PAVI SalesForce:
        query = f"""
                SELECT
                        Id,
                        IsPersonAccount,
                        Name,
                        FirstName,
                        MiddleName,
                        LastName,
                        Gender__c, Birth_Date__c, Civil_Status__c,
                        Home_Ownership__c,
                        Account_Classification__c, Account_Sub_Classification__c,
                        Customer_Type__c,
                        Type, Zone_Type_Acc__c, Zone_Sub_Type_Acc__c,

                        PersonMobilePhone, Mobile_Phone__c,
                        Person_Secondary_Mobile_Number__c, Secondary_Mobile_Number__pc,
                        Phone, Person_Secondary_Phone__c, PersonOtherPhone,

                        Area_Code_BillingAddress__c,
                        Barangay_BillingAddress__c,
                        NameBldg_NoFloor_No_BillingAddress__c,
                        Street_BillingAddress__c,
                        City_BillingAddress__c,
                        Province_BillingAddress__c,
                        Region_BillingAddress__c,

                        Area_Code_BusinessAddress__c,
                        Barangay_BusinessAddress__c,
                        NameBldg_NoFloor_No_BusinessAddress__c,
                        Street_BusinessAddress__c,
                        City_BusinessAddress__c,
                        Province_BusinessAddress__c,
                        Region_BusinessAddress__c,

                        House_No_BL_Phase__c,
                        Barangay_Subdivision_Name__c,
                        City__c,
                        Province__c,
                        Region__c,
                        Person_Contact_Name__c,

                        PersonEmail,
                        Person_Secondary_Email_Address__c,
                        Secondary_Email_Address__pc
                    FROM Account
                    WHERE Id != null
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

        query += " LIMIT 10000 "
        contacts = self.sales_force.bulk.Account.query(query)
        return self.creating_contacts(contacts)

    def _create_customer(self, partner, lead_partner, zone=None):
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

        if zone:
            data['subscriber_location_id'] = zone.id

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

        lead_partner.action_assign_customer_id()

        return lead_partner

    def creating_contacts(self, contacts):
        try:
            salesforce_ids = []
            parent = None
            for contact in contacts:
                parent = self.env['res.partner'].search([('salesforce_id', '=', contact['Id'])])
                lead_partner = self._create_customer(contact, parent)

                self.env.cr.commit()
                salesforce_ids.append(contact['Id'])
            return salesforce_ids

        except Exception as e:
            raise osv.except_osv("Error Details!", e)
