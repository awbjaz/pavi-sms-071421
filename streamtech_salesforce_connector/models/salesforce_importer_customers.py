import logging
import datetime

from odoo import models
from openerp.osv import osv

_logger = logging.getLogger(__name__)


class SalesForceImporterCustomers(models.Model):
    _inherit = 'salesforce.connector'

    def import_customers(self, Auto):
        _logger.info('----------------- STREAMTECH import_customers')
        try:
            if not self.sales_force:
                self.connect_to_salesforce()

            # end = datetime.datetime.now(pytz.UTC)
            # updated_ids = self.sales_force.Contact.updated(end - datetime.timedelta(days=28), end)['ids']

            # Field/s changed due to errors found with usage with PAVI SalesForce: 
            #  OtherStreet -> MailingStreet
            #  OtherCity -> MailingCity
            #  OtherPostalCode -> MailingPostalCode
            #  OtherCountry -> MailingCountry
            #
            # Note:
            #  - These MailingXXX fields have been observed to get only populated for Corporate Account's Contacts
            #  - Other information like Gender and birthdate information are in Account table and not in Contact
            #    and some of them are PAVI custom fields and not present by default in SalesForce
            query = """
                SELECT 
                    id, FirstName, MiddleName, LastName, email, MailingStreet, MailingCity, MailingPostalCode, MailingCountry,
                    fax, phone, LastMOdifiedDate, AccountId 
                FROM Contact
                """

            if not Auto:
                if not self.from_date and not self.to_date:
                    pass

                elif not self.from_date and self.to_date:
                    raise osv.except_osv("Warning!", "Sorry; invalid operation, please select From Date")

                elif self.from_date and not self.to_date:
                    from_date_query = " WHERE CreatedDate>= " + self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                    query = query + from_date_query

                elif self.from_date and self.to_date:
                    from_date_query = " WHERE CreatedDate>= " + self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                    to_date_query = " AND createdDate<=" + self.to_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                    query = query + from_date_query + to_date_query
            else:
                today = datetime.date.today()
                yesterday = today - datetime.timedelta(days=1)
                from_date_query = " WHERE CreatedDate>=" + yesterday.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                to_date_query = " AND createdDate<=" + today.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                query = query + from_date_query + to_date_query

            contacts = self.sales_force.query(query)['records']

            # TODO: uncomment
            return self.creating_contacts(contacts)

            # TODO: remove
            # return []

        except Exception as e:
            _logger.error(e, exc_info=True)
            raise osv.except_osv("Error Details!", e)

    def _get_value(self, obj, key, alt=None):
        value = obj.get(key, alt)
        if value:
            try:
                value = value.lower()
            except:
                pass
        return value

    def _create_partner_data(self, sf_account, is_company, employee_contact = None):

        street = None
        city = None
        brgy = None
        province = None
        region = None

        extra_fields = {}

        # For SF residential accounts
        if not is_company:
            name = '%s %s %s' % (sf_account['FirstName'], sf_account['MiddleName'], sf_account['LastName'])  

            if employee_contact is not None:
                street = employee_contact.get('MailingStreet')
                brgy = None
                city = employee_contact.get('MailingCity')
                country = employee_contact.get('MailingCountry')

            else:
                street = sf_account.get('House_No_BL_Phase__c')
                brgy = sf_account.get('Barangay_Subdivision_Name__c')
                city = sf_account.get('City__c')
                province = sf_account.get('Province__c')
                region = sf_account.get('Region__c')

            extra_fields = {
                'first_name': sf_account.get('FirstName'),
                'middle_name': sf_account.get('MiddleName'),
                'last_name': sf_account.get('LastName')
            }

        # For SF corporate accounts
        else:
            name = sf_account.get('Name')

            bldg_business = sf_account.get('NameBldg_NoFloor_No_BusinessAddress__c')
            street_business = sf_account.get('Street_BusinessAddress__c')
            brgy_business = sf_account.get('Barangay_BusinessAddress__c')
            city_business = sf_account.get('City_BusinessAddress__c')
            province_business = sf_account.get('Province_BusinessAddress__c')
            region_business = sf_account.get('Region_BusinessAddress__c')

            bldg_billing = sf_account.get('NameBldg_NoFloor_No_BillingAddress__c')
            street_billing = sf_account.get('Street_BillingAddress__c')
            brgy_billing = sf_account.get('Barangay_BillingAddress__c')
            city_billing = sf_account.get('City_BillingAddress__c')
            province_billing = sf_account.get('Province_BillingAddress__c')
            region_billing = sf_account.get('Region_BillingAddress__c')

            street = street_billing
            city = city_billing
            brgy = brgy_billing
            province = province_billing
            region = region_billing

        mobile1 = sf_account.get('PersonMobilePhone', sf_account.get('Mobile_Phone__c'))
        mobile2 = sf_account.get('Person_Secondary_Mobile_Number__c', sf_account.get('Secondary_Mobile_Number__pc'))

        phone1 = sf_account.get('PersonMobilePhone')
        phone2 = sf_account.get('Person_Secondary_Phone__c', sf_account.get('PersonOtherPhone'))

        # TODO: 
        # add support for adding both billing and business address information of corporate accounts
        # add support for phone2, mobile, mobile2

        data = {
            'salesforce_id': employee_contact['Id'] if employee_contact else sf_account['Id'],
            'name': name,
            'street': street,
            'street2': brgy,
            'city': city,
            # 'country.state': province,
            #'region': region,
            'phone': phone1,
            'is_company': is_company,

            'home_ownership': self._get_value(sf_account, 'Home_Ownership__c'),
            'gender': self._get_value(sf_account, 'Gender__c'),
            'birthday': sf_account.get('Birth_Date__c'),

            # 'account_classification': self._get_value(sf_account, 'Account_Classification__c'),
            # 'account_subclassification': self._get_value(sf_account, 'Account_Sub_Classification__c'),
            # 'subscriber_type': self._get_value(sf_account, 'Customer_Type__c'),
            # 'account_type': self._get_value(sf_account, 'Type'),
            # 'account_group': self._get_value(sf_account, 'Zone_Type_Acc__c'),
            # 'zone_type': self._get_value(sf_account, 'Zone_Type_Acc__c'),
            # 'zone_subtype': self._get_value(sf_account, 'Zone_Sub_Type_Acc__c'),
            #'category': 'existing'              # TODO: determine new or existing 
        }

        # Add to data the extra fields
        data.update(extra_fields)

        return data


    def creating_contacts(self, contacts):
        """Create contacts on Odoo based on data from PAVI Streamtech-specific SalesForce data entries.
        
        Some pecularities:
        - Corporate Accounts do not have email non-blank values
        - SF standard fields like ShippingXXX, BillingXXX fields are not used at all
        - Custom fields however are added for the address information. 
        - Inconsistent location of address information. Address fiels is different for the following entities:
            - Non-Corporate Accounts
            - Corporate Accounts 
            - Contacts under Corporate Account 
              - these are the primary source for email information for Corporate Account

        Address Fields for Non-Corporate Accounts
            -  
        """

        _logger.info('----------------- STREAMTECH creating_contacts')
        try:
            salesforce_ids = []
            parent = None

            for contact in contacts:
                if not contact['AccountId']:
                    # TODO: add in fail/ignored/unprocessed listing of entries 
                    pass

                sf_account = None

                query = """
                    SELECT 
                        Id, 
                        IsPersonAccount,
                        Name,
                        FirstName, 
                        MiddleName, 
                        LastName, 

                        Gender__c,
                        Birth_Date__c,
                        Home_Ownership__c,

                        Account_Classification__c,
                        Account_Sub_Classification__c,
                        Customer_Type__c,
                        Type,
                        Zone_Type_Acc__c,
                        Zone_Sub_Type_Acc__c,

                        PersonMobilePhone,
                        Mobile_Phone__c,
                        Person_Secondary_Mobile_Number__c,
                        Secondary_Mobile_Number__pc,

                        Phone,
                        Person_Secondary_Phone__c,
                        PersonOtherPhone,

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
                    """
                extend_query = " WHERE id='" + contact['AccountId'] + "'"

                # Fetch SF Account data
                sf_account = self.sales_force.query(query + extend_query)["records"][0]

                # Determine if residential or corporate account
                is_company = sf_account['IsPersonAccount'] is False  

                # Find corresponding Odoo Account
                parent = self.env['res.partner'].search([('salesforce_id', '=', contact['AccountId'])])

                # If no Odoo Partner data for the SF Account
                if not parent:
                    partner = self._create_partner_data(sf_account, is_company)
                    partner['location'] = 'SalesForce Contact'
                    partner['customer_rank'] = 1
                    parent = self.env['res.partner'].create(partner)
                    self.env.cr.commit()

                # If corporate account, then create contact for the employee
                if is_company:
                    child = self.env['res.partner'].search([('salesforce_id', '=', contact['Id'])])

                    employee_contact = contact
                    child_data = self._create_partner_data(sf_account, False, employee_contact)
                    child_data['parent_id'] = parent[0].id if parent else None

                    # If no Odoo Partner data for the SF Contact
                    if not child:
                        child_data['last_modified'] = contact['LastModifiedDate']
                        child_data['location']: 'SalesForce Contact'
                        self.env['res.partner'].create(child_data)

                    # elif child['salesforce_id'] in updated_ids:
                    elif child.last_modified != contact['LastModifiedDate']:
                        child.write(child_data)

                    self.env.cr.commit()
                    salesforce_ids.append(contact['Id'])
            return salesforce_ids

        except Exception as e:
            raise osv.except_osv("Error Details!", e)
