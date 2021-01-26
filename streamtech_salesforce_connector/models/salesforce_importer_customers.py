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

                        PersonMobilePhone,
                        Mobile_Phone__c,

                        Area_Code_BillingAddress__c,
                        Barangay_BillingAddress__c,
                        NameBldg_NoFloor_No_BillingAddress__c,
                        Street_BillingAddress__c,
                        City_BillingAddress__c,
                        Province_BillingAddress__c,
                        Region_BillingAddress__c,

                        House_No_BL_Phase__c,
                        Barangay_Subdivision_Name__c,
                        City__c,
                        Province__c,
                        Region__c,
                        Person_Contact_Name__c,

                        Birth_Date__c,
                        Gender__c,
                        Home_Ownership__c,

                        PersonEmail,
                        Person_Secondary_Email_Address__c,
                        Secondary_Email_Address__pc
                    FROM Account
                    """
                extend_query = " WHERE id='" + contact['AccountId'] + "'"

                # Fetch SF Account data
                sf_account = self.sales_force.query(query + extend_query)["records"][0]

                parent = self.env['res.partner'].search([('salesforce_id', '=', contact['AccountId'])])

                if not parent:
                    parent = self.env['res.partner'].create({
                        'salesforce_id': sf_account['Id'],
                        'name': sf_account['Name'],
                        'city': sf_account['City_BillingAddress__c'] if sf_account['City_BillingAddress__c'] else None,
                        'street': sf_account['Street_BillingAddress__c'] if sf_account['Street_BillingAddress__c'] else None,
                        'zip': sf_account['Area_Code_BillingAddress__c'] if sf_account['Area_Code_BillingAddress__c'] else None,
                        'phone': sf_account['Phone'] if sf_account['PersonMobilePhone'] else sf_account['Mobile_Phone__c'],
                        'location': 'SalesForce Contact',
                        'is_company': True,
                        'customer_rank': 1,
                    })
                    self.env.cr.commit()

                if contact['FirstName']:
                    name = contact['FirstName'] + " " + contact['LastName']
                else:
                    name = contact['LastName']
                child = self.env['res.partner'].search([('salesforce_id', '=', contact['Id'])])

                child_data = {
                        'salesforce_id': contact['Id'],
                        'name': name,
                        'first_name': contact['FirstName'] if contact['FirstName'] else None,
                        'last_name': contact['LastName'] if contact['LastName'] else None,
                        'street': contact['MailingStreet'] if contact['MailingStreet'] else sf_account['House_No_BL_Phase__c'] + ' ' + sf_account['Barangay_Subdivision_Name__c'],
                        'zip': contact['MailingPostalCode'] if contact['MailingPostalCode'] else sf_account['Area_Code_BillingAddress__c'],
                        'phone': sf_account['Phone'] if sf_account['PersonMobilePhone'] else sf_account['Mobile_Phone__c'],
                        'is_company': False,
                        'parent_id': parent[0].id if parent else None,
                    }

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
