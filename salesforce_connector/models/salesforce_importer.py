from odoo import models, fields, api, exceptions, _
from simple_salesforce import Salesforce
from openerp import _
from openerp.osv import osv
from openerp.exceptions import Warning
import datetime
import os
import json
import pytz

class SalesForceImporter(models.Model):
    _name = 'salesforce.connector'

    sales_force = None
    field_name = fields.Char('salesforce_connector')
    history_line = fields.One2many('sync.history', 'sync_id', copy=True)
    customers = fields.Boolean('Import Customers')
    sales_orders = fields.Boolean('Import Sale Orders')
    products = fields.Boolean('Import Products')
    opportunities = fields.Boolean('Import Opportunities')
    leads = fields.Boolean('Import Leads')
    tasks = fields.Boolean('Import Tasks')
    calendars = fields.Boolean('Import Calendars')
    quotes = fields.Boolean('Import Quotes')
    contracts = fields.Boolean('Import Contracts')
    export_customers = fields.Boolean('Export Customers')
    export_sales_orders = fields.Boolean('Export Sale Orders')
    export_products = fields.Boolean('Export Products')
    export_opportunities = fields.Boolean('Export Opportunities')
    export_leads = fields.Boolean('Export Leads')
    export_tasks = fields.Boolean('Export Tasks')
    export_calendars = fields.Boolean('Export Calendars')
    export_quotes = fields.Boolean('Export Quotes')
    export_contracts = fields.Boolean('Export Contracts')
    custom_sync = fields.Boolean('Custom Sync')
    auto_sync = fields.Boolean('Auto Sync')
    interval_number = fields.Integer(string=_("Interval Number"))
    interval_unit = fields.Selection([
        ('minutes', _('Minutes')),
        ('hours', _('Hours')),
        ('work_days', _('Work Days')),
        ('days', _('Days')),
        ('weeks', _('Weeks')),
        ('months', _('Months')),
    ], string=_('Interval Unit'))
    from_date = fields.Datetime(string='From Date')
    to_date = fields.Datetime(string='To Date')
    last_date = fields.Char(string='Last Sync Date')

    def connect_to_salesforce(self):
        """
        test user connection

        """
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            self.sales_force = Salesforce(username=username, password=password, security_token=security)
        except Exception as e:
            Warning(_(str(e)))

    def execute_operation(self):
        if self.custom_sync or self.auto_sync:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
            if username and password and security and enabler == 'True':
                if self.customers or self.products or self.sales_orders or self.opportunities \
                        or self.leads or self.tasks or self.calendars or self.quotes or self.contracts:
                    if self.custom_sync:
                        self.import_data(False)
                    if self.auto_sync:
                        scheduler = self.env['ir.cron'].search([('name', '=', 'Import Scheduler')])
                        if not scheduler:
                            scheduler = self.env['ir.cron'].search([('name', '=', 'Import Scheduler'),
                                                                    ('active', '=', False)])
                        scheduler.active = self.auto_sync
                        scheduler.interval_number = self.interval_number
                        scheduler.interval_type = self.interval_unit

                if self.export_leads or self.export_opportunities or self.export_sales_orders \
                        or self.export_customers or self.export_quotes or self.export_products:
                    if self.custom_sync:
                        self.export_data(False)
                    if self.auto_sync:
                        scheduler = self.env['ir.cron'].search([('name', '=', 'Export Scheduler')])
                        if not scheduler:
                            scheduler = self.env['ir.cron'].search([('name', '=', 'Export Scheduler'),
                                                                    ('active', '=', False)])
                        scheduler.active = self.auto_sync
                        scheduler.interval_number = self.interval_number
                        scheduler.interval_type = self.interval_unit

                if not self.customers and not self.products and not self.sales_orders and not self.opportunities \
                        and not self.leads and not self.tasks and not self.calendars and not self.quotes and not self.contracts \
                        and not self.export_leads and not self.export_opportunities and not self.export_sales_orders \
                        and not self.export_customers and not self.export_quotes and not self.export_products:
                    raise osv.except_osv("Execution Details!", "No Option Checked.")
            else:
                raise osv.except_osv('', 'Please enter credentials before executing.')
        else:
            raise osv.except_osv('', 'Please specify the type of synchronization.')

    def auto_import(self):
        self.import_data(True)

    def auto_export(self):
        self.export_data(True)

    def import_data(self, Auto):
        data_dictionary = {}
        if Auto:
            self = self.env['salesforce.connector'].search([])[0]

        if self.customers:
            data_dictionary["customers"] = self.import_customers(Auto)
        if self.sales_orders:
            data_dictionary["sales_orders"] = self.import_sale_orders(Auto)
        if self.products:
            data_dictionary["products"] = self.import_products(Auto)
        if self.opportunities:
            data_dictionary["opportinities"] = self.import_opportunities(Auto)
        if self.leads:
            data_dictionary["leads"] = self.import_leads(Auto)
        if self.tasks:
            data_dictionary["tasks"] = self.import_tasks(Auto)
        if self.calendars:
            data_dictionary["calendars"] = self.import_calendars(Auto)
        if self.contracts:
            data_dictionary["contracts"] = self.import_contracts(Auto)
        if self.quotes:
            data_dictionary["quotes"] = self.import_quotes(Auto)
        no_of_customers = len(data_dictionary.get("customers", []))
        no_of_sales_orders = len(data_dictionary.get("sales_orders", []))
        no_of_products = len(data_dictionary.get('products', []))
        no_of_opportunities = len(data_dictionary.get('opportinities', []))
        no_of_leads = len(data_dictionary.get('leads', []))
        no_of_tasks = len(data_dictionary.get('tasks', []))
        no_of_calendars = len(data_dictionary.get('calendars', []))
        no_of_contracts = len(data_dictionary.get('contracts', []))
        no_of_quotes = len(data_dictionary.get('quotes', []))

        if no_of_customers + no_of_products + no_of_sales_orders + no_of_opportunities + \
                no_of_leads + no_of_tasks + no_of_calendars + no_of_quotes + no_of_contracts:
            self.sync_history(no_of_customers, no_of_sales_orders, no_of_products, no_of_opportunities, no_of_leads,
                              no_of_tasks, no_of_calendars, no_of_quotes, no_of_contracts, "Import")

        else:
            raise osv.except_osv(_("Sync Details!"), _("No new sync needed. Data already synced."))

    def export_data(self, Auto):

        data_dictionary = {}
        if Auto:
            self = self.env['salesforce.connector'].search([])[0]

        if self.export_customers:
            data_dictionary["customers"] = self.export_customers_data(Auto)
        if self.export_sales_orders:
            data_dictionary["sales_orders"] = self.export_sales_orders_data(Auto)
        if self.export_products:
            data_dictionary["products"] = self.export_products_data(Auto)
        if self.export_opportunities:
            data_dictionary["opportinities"] = self.export_opportunities_data(Auto)
        if self.export_leads:
            data_dictionary["leads"] = self.export_leads_data(Auto)
        if self.export_quotes:
            data_dictionary["quotes"] = self.export_quotes_data(Auto)

        no_of_customers = len(data_dictionary.get("customers", []))
        no_of_sales_orders = len(data_dictionary.get("sales_orders", []))
        no_of_products = len(data_dictionary.get('products', []))
        no_of_opportunities = len(data_dictionary.get('opportinities', []))
        no_of_leads = len(data_dictionary.get('leads', []))
        no_of_quotes = len(data_dictionary.get('quotes', []))

        if no_of_customers + no_of_products + no_of_sales_orders + no_of_opportunities + \
                no_of_leads + no_of_quotes:
            self.sync_history(no_of_customers, no_of_sales_orders, no_of_products, no_of_opportunities, no_of_leads,
                              0, 0, no_of_quotes, 0, "Export")

        else:
            raise osv.except_osv(_("Sync Details!"), _("No new sync needed. Data already synced."))

    def sync_history(self, no_of_customers, no_of_sales_orders, no_of_products, no_of_opportunities, no_of_leads,
                     no_of_tasks, no_of_calendars, no_of_quotes, no_of_contracts, nature):
        sync_history = self.env["sync.history"]
        sync_history.create({
            "no_of_orders_sync": no_of_sales_orders,
            "no_of_customers_sync": no_of_customers,
            "no_of_products_sync": no_of_products,
            "no_of_opportunities_sync": no_of_opportunities,
            "no_of_leads_sync": no_of_leads,
            "no_of_tasks_sync": no_of_tasks,
            "no_of_calendars_sync": no_of_calendars,
            "no_of_quotes_sync": no_of_quotes,
            "no_of_contracts_sync": no_of_contracts,
            "sync_nature": nature,
            "sync_date": datetime.datetime.now(),
            "sync_id": 1,
        })

        self.env.cr.commit()

    def import_quotes(self, Auto):
        try:
            if not self.sales_force:
                self.connect_to_salesforce()

            if not Auto:
                if not self.from_date and not self.to_date:
                    query = "select id, name, status,LastMOdifiedDate, AccountId, quoteNumber,opportunityId, createdDate,expirationDate from quote"
                    quotes = self.sales_force.query(query)['records']
                    return self.creating_quotes(quotes)

                elif not self.from_date and self.to_date:
                    raise osv.except_osv("Warning!", "Sorry; invalid operation, please select From Date")

                elif self.from_date and not self.to_date:
                    query = "select id, name, status,LastMOdifiedDate, AccountId, quoteNumber,opportunityId, createdDate,expirationDate " \
                            "from quote where CreatedDate>="
                    from_date_query = self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                    quotes = self.sales_force.query(query + from_date_query)['records']
                    return self.creating_quotes(quotes)

                elif self.from_date and self.to_date:
                    query = "select id, name, status,LastMOdifiedDate, AccountId, quoteNumber,opportunityId, createdDate,expirationDate " \
                            "from quote where CreatedDate>="
                    from_date_query = self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                    to_date_query = self.to_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                    quotes = self.sales_force.query(query + from_date_query + " and createdDate<=" + to_date_query)[
                        'records']
                    return self.creating_quotes(quotes)
            else:
                today = datetime.date.today()
                yesterday = today - datetime.timedelta(days=1)

                query = "select id, name, status,LastMOdifiedDate, AccountId, quoteNumber,opportunityId, createdDate,expirationDate " \
                        "from quote where CreatedDate>="
                from_date_query = yesterday.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                to_date_query = today.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                quotes = self.sales_force.query(query + from_date_query + " and createdDate<=" + to_date_query)[
                    'records']
                return self.creating_quotes(quotes)

        except Exception as e:
            raise osv.except_osv("Error Details!", e)

    def import_sale_orders(self, Auto):
        try:
            if not self.sales_force:
                self.connect_to_salesforce()

            if not Auto:
                if not self.from_date and not self.to_date:
                    query = "select id , AccountId, EffectiveDate, ContractId," \
                            "orderNumber, status,LastMOdifiedDate, CreatedDate from Order"
                    orders = self.sales_force.query(query)['records']
                    return self.creating_orders(orders)

                elif not self.from_date and self.to_date:
                    raise osv.except_osv("Warning!", "Sorry; invalid operation, please select From Date")

                elif self.from_date and not self.to_date:
                    query = "select id , AccountId, EffectiveDate, ContractId," \
                            "orderNumber, status,LastMOdifiedDate, CreatedDate from Order where CreatedDate>="
                    from_date_query = self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                    orders = self.sales_force.query(query + from_date_query)['records']
                    return self.creating_orders(orders)

                elif self.from_date and self.to_date:
                    query = "select id , AccountId, EffectiveDate, ContractId," \
                            "orderNumber, status,LastMOdifiedDate, CreatedDate from Order where CreatedDate>="
                    from_date_query = self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                    to_date_query = self.to_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                    orders = self.sales_force.query(query + from_date_query + " and createdDate<=" + to_date_query)[
                        'records']
                    return self.creating_orders(orders)
            else:
                today = datetime.date.today()
                yesterday = today - datetime.timedelta(days=1)
                query = "select id , AccountId, EffectiveDate, ContractId," \
                        "orderNumber, status,LastMOdifiedDate, CreatedDate from Order where CreatedDate>="
                from_date_query = yesterday.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                to_date_query = today.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                orders = self.sales_force.query(query + from_date_query + " and createdDate<=" + to_date_query)[
                    'records']
                return self.creating_orders(orders)

        except Exception as e:
            raise osv.except_osv("Error Details!", e)

    def import_products(self, Auto):
        try:
            if not self.sales_force:
                self.connect_to_salesforce()

            if not Auto:
                if not self.from_date and not self.to_date:
                    query = "SELECT Product2.Id, Product2.Name, Product2.ProductCode, Product2.Description, Product2.Family" \
                            ", Product2.CreatedDate,LastMOdifiedDate, UnitPrice from PriceBookEntry"
                    products = self.sales_force.query(query)['records']
                    return self.creating_products(products)

                elif not self.from_date and self.to_date:
                    raise osv.except_osv("Warning!", "Sorry; invalid operation, please select From Date")

                elif self.from_date and not self.to_date:
                    query = "SELECT Product2.Id, Product2.Name, Product2.ProductCode, Product2.Description, Product2.Family" \
                            ", Product2.CreatedDate,LastMOdifiedDate, UnitPrice from PriceBookEntry where Product2.CreatedDate>="
                    from_date_query = self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                    products = self.sales_force.query(query + from_date_query)['records']
                    return self.creating_products(products)

                elif self.from_date and self.to_date:
                    query = "SELECT Product2.Id, Product2.Name, Product2.ProductCode, Product2.Description, Product2.Family" \
                            ", Product2.CreatedDate,LastMOdifiedDate, UnitPrice from PriceBookEntry where Product2.CreatedDate>="
                    from_date_query = self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                    to_date_query = self.to_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                    products = \
                    self.sales_force.query(query + from_date_query + " and Product2.CreatedDate<=" + to_date_query)[
                        'records']
                    return self.creating_products(products)
            else:
                today = datetime.date.today()
                yesterday = today - datetime.timedelta(days=1)
                query = "SELECT Product2.Id, Product2.Name, Product2.ProductCode, Product2.Description, Product2.Family" \
                        ", Product2.CreatedDate,LastMOdifiedDate, UnitPrice from PriceBookEntry where Product2.CreatedDate>="
                from_date_query = yesterday.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                to_date_query = today.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                products = \
                    self.sales_force.query(query + from_date_query + " and Product2.CreatedDate<=" + to_date_query)[
                        'records']
                return self.creating_products(products)

        except Exception as e:
            raise osv.except_osv("Error Details!", e)

    def import_customers(self, Auto):
        try:
            if not self.sales_force:
                self.connect_to_salesforce()

            # end = datetime.datetime.now(pytz.UTC)
            # updated_ids = self.sales_force.Contact.updated(end - datetime.timedelta(days=28), end)['ids']

            if not Auto:
                if not self.from_date and not self.to_date:
                    query = "select id, FirstName,LastName,email, OtherStreet,OtherCity, OtherPostalCode, OtherCountry," \
                            "fax, phone,LastMOdifiedDate, AccountId from Contact"
                    contacts = self.sales_force.query(query)['records']
                    return self.creating_contacts(contacts)

                elif not self.from_date and self.to_date:

                    raise osv.except_osv("Warning!", "Sorry; invalid operation, please select From Date")

                elif self.from_date and not self.to_date:
                    query = "select id, FirstName,LastName,email, OtherStreet,OtherCity, OtherPostalCode, OtherCountry," \
                            "fax, phone,LastMOdifiedDate, AccountId from Contact where CreatedDate>="
                    from_date_query = self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                    contacts = self.sales_force.query(query + from_date_query)['records']
                    return self.creating_contacts(contacts)

                elif self.from_date and self.to_date:
                    query = "select id, FirstName,LastName,email, OtherStreet,OtherCity, OtherPostalCode, OtherCountry," \
                            "fax, phone,CreatedDate,LastMOdifiedDate, AccountId from Contact where CreatedDate>="
                    from_date_query = self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                    to_date_query = self.to_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                    contacts = self.sales_force.query(query + from_date_query + " and createdDate<=" + to_date_query)[
                        'records']

                    return self.creating_contacts(contacts )
            else:
                today = datetime.date.today()
                yesterday = today - datetime.timedelta(days=1)
                query = "select id, FirstName,LastName,email, OtherStreet,OtherCity, OtherPostalCode, OtherCountry," \
                        "fax, phone,LastMOdifiedDate, AccountId from Contact where CreatedDate>="
                from_date_query = yesterday.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                to_date_query = today.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                contacts = self.sales_force.query(query + from_date_query + " and createdDate<=" + to_date_query)[
                    'records']
                return self.creating_contacts(contacts)

        except Exception as e:
            raise osv.except_osv("Error Details!", e)

    def import_opportunities(self, Auto):
        try:
            if not self.sales_force:
                self.connect_to_salesforce()

            if not Auto:
                if not self.from_date and not self.to_date:
                    query = "select id,name, AccountId, Amount, CloseDate, \
                            Description, ExpectedRevenue, HasOpenActivity, IsDeleted, \
                            IsWon,OwnerId,LastMOdifiedDate, Probability, LastActivityDate, StageName, type, leadSource," \
                            "CampaignId from opportunity"
                    opportunities = self.sales_force.query(query)['records']
                    return self.creating_opportunities(opportunities)

                elif not self.from_date and self.to_date:
                    raise osv.except_osv("Warning!", "Sorry; invalid operation, please select From Date")

                elif self.from_date and not self.to_date:
                    query = "select id,name, AccountId, Amount, CloseDate, \
                            Description,LastMOdifiedDate, ExpectedRevenue, HasOpenActivity, IsDeleted, \
                            IsWon,OwnerId, Probability, LastActivityDate, StageName, type, leadSource," \
                            "CampaignId from opportunity where CreatedDate>="
                    from_date_query = self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                    opportunities = self.sales_force.query(query + from_date_query)['records']
                    return self.creating_opportunities(opportunities)

                elif self.from_date and self.to_date:
                    query = "select id,name, AccountId, Amount, CloseDate, \
                            Description,LastMOdifiedDate, ExpectedRevenue, HasOpenActivity, IsDeleted, \
                            IsWon,OwnerId, Probability, LastActivityDate, StageName, type, leadSource," \
                            "CampaignId from opportunity where CreatedDate>="
                    from_date_query = self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                    to_date_query = self.to_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                    opportunities = self.sales_force.query(query + from_date_query + " and createdDate<=" + to_date_query)[
                        'records']
                    return self.creating_opportunities(opportunities)
            else:
                today = datetime.date.today()
                yesterday = today - datetime.timedelta(days=1)
                query = "select id,name, AccountId, Amount,LastMOdifiedDate, CloseDate, \
                                            Description, ExpectedRevenue, HasOpenActivity, IsDeleted, \
                                            IsWon,OwnerId, Probability, LastActivityDate, StageName, type, leadSource," \
                        "CampaignId from opportunity where CreatedDate>="
                from_date_query = yesterday.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                to_date_query = today.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                opportunities = self.sales_force.query(query + from_date_query + " and createdDate<=" + to_date_query)[
                    'records']
                return self.creating_opportunities(opportunities)

        except Exception as e:
            raise osv.except_osv("Error Details!", e)

    def import_leads(self, Auto):
        try:
            if not self.sales_force:
                self.connect_to_salesforce()

            if not Auto:
                if not self.from_date and not self.to_date:
                    query = "select id, salutation, FirstName, LastName,phone,company, title" \
                            ",fax, email, LeadSource, Industry,status,rating, city, PostalCode," \
                            " country, street,LastMOdifiedDate, state, AnnualRevenue, description" \
                            " from lead"
                    leads = self.sales_force.query(query)['records']
                    return self.creating_leads(leads)

                elif not self.from_date and self.to_date:
                    raise osv.except_osv("Warning!", "Sorry; invalid operation, please select From Date")

                elif self.from_date and not self.to_date:
                    query = "select id, salutation, FirstName, LastName,phone,company, title" \
                            ",fax, email, LeadSource, Industry,status,rating, city, PostalCode," \
                            " country, street,LastMOdifiedDate, state, AnnualRevenue, description" \
                            " from lead where CreatedDate>="
                    from_date_query = self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                    leads = self.sales_force.query(query + from_date_query)['records']
                    return self.creating_leads(leads)
                elif self.from_date and self.to_date:
                    query = "select id, salutation, FirstName, LastName,phone,company, title" \
                            ",fax, email, LeadSource, Industry,status,rating, city, PostalCode," \
                            " country, street,LastMOdifiedDate, state, AnnualRevenue, description" \
                            " from lead where CreatedDate>="
                    from_date_query = self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                    to_date_query = self.to_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                    leads = self.sales_force.query(query + from_date_query + " and createdDate<=" + to_date_query)[
                        'records']
                    return self.creating_leads(leads)
            else:
                today = datetime.date.today()
                yesterday = today - datetime.timedelta(days=1)
                query = "select id, salutation, FirstName, LastName,phone,company, title" \
                        ",fax, email, LeadSource, Industry,status,rating, city, PostalCode," \
                        " country, street,LastMOdifiedDate, state, AnnualRevenue, description" \
                        " from lead where CreatedDate>="
                from_date_query = yesterday.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                to_date_query = today.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                leads = self.sales_force.query(query + from_date_query + " and createdDate<=" + to_date_query)[
                    'records']
                return self.creating_leads(leads)

        except Exception as e:
            raise osv.except_osv("Error Details!", e)

    def import_tasks(self, Auto):
        try:
            if not self.sales_force:
                self.connect_to_salesforce()

            if not Auto:
                if not self.from_date and not self.to_date:
                    query = "select id, subject, status, priority, description, ActivityDate," \
                            "WhatId,LastMOdifiedDate, WhoId, OwnerId from task"
                    tasks = self.sales_force.query(query)['records']
                    return self.creating_tasks(tasks)

                elif not self.from_date and self.to_date:
                    raise osv.except_osv("Warning!", "Sorry; invalid operation, please select From Date")

                elif self.from_date and not self.to_date:
                    query = "select id, subject, status, priority, description, ActivityDate," \
                            "WhatId,LastMOdifiedDate, WhoId, OwnerId from task where CreatedDate>="
                    from_date_query = self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                    tasks = self.sales_force.query(query + from_date_query)['records']
                    return self.creating_tasks(tasks)
                elif self.from_date and self.to_date:
                    query = "select id, subject, status, priority, description, ActivityDate," \
                            "WhatId,LastMOdifiedDate, WhoId, OwnerId from task where CreatedDate>="
                    from_date_query = self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                    to_date_query = self.to_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                    tasks = self.sales_force.query(query + from_date_query + " and createdDate<=" + to_date_query)[
                        'records']
                    return self.creating_tasks(tasks)
            else:
                today = datetime.date.today()
                yesterday = today - datetime.timedelta(days=1)
                query = "select id, subject, status, priority, description, ActivityDate," \
                        "WhatId,LastMOdifiedDate, WhoId, OwnerId from task where CreatedDate>="
                from_date_query = yesterday.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                to_date_query = today.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                tasks = self.sales_force.query(query + from_date_query + " and createdDate<=" + to_date_query)[
                    'records']
                return self.creating_tasks(tasks)

        except Exception as e:
            raise osv.except_osv("Error Details!", e)

    def import_calendars(self, Auto):
        try:
            if not self.sales_force:
                self.connect_to_salesforce()

            if not Auto:
                if not self.from_date and not self.to_date:
                    query = "select id, subject,WhoId,description,OwnerId,StartDateTime," \
                            " EndDateTime,LastMOdifiedDate,IsAllDayEvent,location from event"
                    calendars = self.sales_force.query(query)['records']
                    return self.creating_calendars(calendars )

                elif not self.from_date and self.to_date:
                    raise osv.except_osv("Warning!", "Sorry; invalid operation, please select From Date")

                elif self.from_date and not self.to_date:
                    query = "select id, subject,WhoId,description,OwnerId,StartDateTime, " \
                            "EndDateTime,LastMOdifiedDate,IsAllDayEvent,location, CreatedDate from event where CreatedDate>="
                    from_date_query = self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                    calendars = self.sales_force.query(query + from_date_query)['records']
                    return self.creating_calendars(calendars )
                elif self.from_date and self.to_date:
                    query = "select id, subject,WhoId,description,OwnerId,StartDateTime, " \
                            "EndDateTime,LastMOdifiedDate,IsAllDayEvent,location, CreatedDate from event where CreatedDate>="
                    from_date_query = self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                    to_date_query = self.to_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                    calendars = self.sales_force.query(query + from_date_query + " and createdDate<=" + to_date_query)[
                        'records']
                    return self.creating_calendars(calendars )
            else:
                today = datetime.date.today()
                yesterday = today - datetime.timedelta(days=1)
                query = "select id, subject,WhoId,description,OwnerId,StartDateTime, " \
                        "EndDateTime,LastMOdifiedDate,IsAllDayEvent,location, CreatedDate from event where CreatedDate>="
                from_date_query = yesterday.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                to_date_query = today.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                calendars = self.sales_force.query(query + from_date_query + " and createdDate<=" + to_date_query)[
                    'records']
                return self.creating_calendars(calendars)

        except Exception as e:
            raise osv.except_osv("Error Details!", e)

    def import_contracts(self, Auto):
        try:
            if not self.sales_force:
                self.connect_to_salesforce()

            if not Auto:
                if not self.from_date and not self.to_date:
                    query = "select id, AccountId, status, startDate,LastMOdifiedDate, contractTerm, contractNumber" \
                            " from contract"
                    contract = self.sales_force.query(query)['records']
                    return self.creating_contracts(contract)

                elif not self.from_date and self.to_date:
                    raise osv.except_osv("Warning!", "Sorry; invalid operation, please select From Date")

                elif self.from_date and not self.to_date:
                    query = "select id, AccountId, status,LastMOdifiedDate, startDate, contractTerm, contractNumber" \
                            " from contract where CreatedDate>="
                    from_date_query = self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                    contract = self.sales_force.query(query + from_date_query)['records']
                    return self.creating_contracts(contract)
                elif self.from_date and self.to_date:
                    query = "select id, AccountId, status,LastMOdifiedDate, startDate, contractTerm, contractNumber" \
                            " from contract where CreatedDate>="
                    from_date_query = self.from_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                    to_date_query = self.to_date.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                    contract = self.sales_force.query(query + from_date_query + " and createdDate<=" + to_date_query)[
                        'records']
                    return self.creating_contracts(contract)
            else:
                today = datetime.date.today()
                yesterday = today - datetime.timedelta(days=1)
                query = "select id, AccountId,LastMOdifiedDate, status, startDate, contractTerm, contractNumber" \
                        " from contract where CreatedDate>="
                from_date_query = yesterday.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"
                to_date_query = today.strftime("%Y-%m-%dT%H:%M:%S") + "+0000"

                contract = self.sales_force.query(query + from_date_query + " and createdDate<=" + to_date_query)[
                    'records']
                return self.creating_contracts(contract)

        except Exception as e:
            raise osv.except_osv("Error Details!", e)

    def creating_quotes(self, quotes):
        try:
            salesforce_ids = []
            for quote in quotes:
                order_partner = self.env['res.partner'].search([('salesforce_id', '=', quote['AccountId'])])[0]
                if not order_partner:
                    query = "select id, name, shippingStreet," \
                            "ShippingCity,Website, " \
                            "ShippingPostalCode, shippingCountry, " \
                            "fax, phone, Description from account"

                    extend_query = " where id='" + quote['AccountId'] + "'"
                    order_partner_new = self.sales_force.query(query + extend_query)["records"][0]
                    order_partner = self.env['res.partner'].create({
                        'salesforce_id': order_partner_new['Id'],
                        'name': order_partner_new['Name'],
                        'location': 'SalesForce Quote Account',
                        'city': order_partner_new['ShippingCity'] if order_partner_new['ShippingCity'] else None,
                        'street': order_partner_new['ShippingStreet'] if order_partner_new['ShippingStreet'] else None,
                        'country_id': self.env['res.country'].search(
                            [('name', '=', order_partner_new['ShippingCountry'])]).id if
                        order_partner_new['ShippingCountry'] else None,
                        'zip': order_partner_new['ShippingPostalCode'] if order_partner_new[
                            'ShippingPostalCode'] else None,
                        'phone': order_partner_new['Phone'] if order_partner_new['Phone'] else None,
                        'is_company': True,
                    })
                    self.env.cr.commit()
                quote_opportunity = self.env['crm.lead'].search([('salesforce_id', '=', quote['OpportunityId'])])
                if not quote_opportunity:
                    query = "select id,name, AccountId, Amount, CloseDate, " \
                            "Description, ExpectedRevenue, HasOpenActivity, IsDeleted, " \
                            "IsWon,OwnerId, Probability, LastActivityDate, StageName, type, leadSource," \
                            "CampaignId from opportunity"

                    extend_query = " where id='" + quote['OpportunityId'] + "'"
                    opportunities = self.sales_force.query(query)['records'][0]
                    if opportunities['AccountId']:
                        lead_partner = self.env['res.partner'].search([('salesforce_id', '=', opportunities['AccountId'])])
                        if not lead_partner:
                            query = "select id, name, shippingStreet," \
                                    "ShippingCity,Website, " \
                                    "ShippingPostalCode, shippingCountry, " \
                                    "fax, phone, Description from account"

                            extend_query = " where id='" + opportunities['AccountId'] + "'"
                            partner = self.sales_force.query(query + extend_query)["records"][0]
                            lead_partner = self.env['res.partner'].create({
                                'salesforce_id': partner['Id'],
                                'name': partner['Name'],
                                'location': 'SalesForce Quote Account',
                                'city': partner['ShippingCity'] if partner['ShippingCity'] else None,
                                'street': partner['ShippingStreet'] if partner['ShippingStreet'] else None,
                                'country_id': self.env['res.country'].search(
                                    [('name', '=', partner['ShippingCountry'])]).id if
                                partner['ShippingCountry'] else None,
                                'zip': partner['ShippingPostalCode'] if partner['ShippingPostalCode'] else None,
                                'phone': partner['Phone'] if partner['Phone'] else None,
                                'is_company': True,
                                'customer': True,

                            })
                        oppor_stage = self.env['crm.stage'].search([('name', '=', opportunities['StageName'])])
                        if not oppor_stage:
                            oppor_stage = self.env['crm.stage'].create({
                                'name': opportunities['StageName'],
                            })

                        quote_opportunity = self.ev['crm.lead'].create({
                            'salesforce_id': opportunities['Id'],
                            'name': opportunities['Name'],
                            'partner_id': lead_partner.id,
                            'location': 'SalesForce',
                            'planned_revenue': opportunities['Amount'] if opportunities['Amount'] else None,
                            'probability': opportunities['Probability'] if opportunities['Probability'] else None,
                            'type': 'opportunity',
                            'date_closed': opportunities['CloseDate'] if opportunities['CloseDate'] else None,
                            'stage_id': oppor_stage.id,
                            'description': opportunities['Description'] if opportunities['Description'] else None,
                            'sf_type': opportunities['Type'] if opportunities['Type'] else None
                        })
                        self.env.cr.commit()
                odoo_order = self.env['sale.order'].search([('salesforce_id_qo', '=', quote['Id'])])
                if not odoo_order:
                    odoo_order = self.env['sale.order'].create({
                        'salesforce_id_qo': quote['Id'],
                        "name": quote["QuoteNumber"],
                        'sf_name': quote['Name'],
                        "partner_id": order_partner.id,
                        "state": 'draft',
                        "sf_status_qo": quote['Status'],
                        "invoice_status": "no",
                        'location': 'SalesForce',
                        "date_order": quote['ExpirationDate'],
                        'opportunity_id': quote_opportunity.id if quote_opportunity else '',
                        'last_modified': quote['LastModifiedDate'],
                    })
                    order_lines = self.sales_force.query("select Pricebookentry.Product2Id , listprice, Quantity from "
                                                         "quotelineitem where quoteid='%s'" % str(quote['Id']))[
                        "records"]
                    for order_line in order_lines:
                        product_id = order_line["PricebookEntry"]["Product2Id"]
                        order_product = self.env['product.template'].search([('salesforce_id', '=', product_id)])
                        if not order_product:
                            order_product_new = self.sales_force.query("SELECT Product2.Id, Product2.Name, "
                                                                       "Product2.ProductCode, Product2.Description,"
                                                                       " Product2.Family,UnitPrice from PriceBookEntry "
                                                                       "where Product2.Id='%s'" % str(product_id))[
                                "records"][0]
                            order_product = self.env['product.template'].create({
                                'salesforce_id': order_product_new['Product2']["Id"],
                                'name': order_product_new['Product2']["Name"],
                                'location': 'SalesForce',
                                'description': order_product_new['Product2']["Description"],
                                'default_code': order_product_new['Product2']["ProductCode"],
                                'list_price': order_product_new['UnitPrice'],
                                'invoice_policy': "delivery",
                            })

                            odoo_product = self.env['product.product'].search(
                                [('product_tmpl_id', '=', order_product.id)])
                            if not odoo_product:
                                self.env['product.product'].create({
                                    'product_tmpl_id': order_product.id
                                })
                                self.env.cr.commit()
                            else:
                                odoo_product.write({
                                    'product_tmpl_id': order_product.id
                                })

                        else:
                            odoo_product = self.env['product.product'].search([('product_tmpl_id',
                                                                                '=',
                                                                                order_product.id)])
                            if not odoo_product:
                                odoo_product = self.env['product.product'].create({
                                    'product_tmpl_id': order_product.id
                                })
                                self.env.cr.commit()

                        self.env['sale.order.line'].create({
                            'product_id': odoo_product[0].id,
                            'order_partner_id': order_partner.id,
                            "order_id": odoo_order.id,
                            "product_uom_qty": order_line['Quantity'],
                            'price_unit': order_line['ListPrice'],
                        })
                    self.env.cr.commit()
                elif odoo_order.last_modified != quote['LastModifiedDate']:
                    odoo_order.write({
                        'salesforce_id_qo': quote['Id'],
                        "name": quote["QuoteNumber"],
                        'sf_name': quote['Name'],
                        "partner_id": order_partner.id,
                        "state": 'draft',
                        "sf_status_qo": quote['Status'],
                        "invoice_status": "no",
                        "date_order": quote['ExpirationDate'],
                        'opportunity_id': quote_opportunity.id,
                        'last_modified': quote['LastModifiedDate'],
                    })
                    self.env.cr.commit()
                salesforce_ids.append(quote['Id'])

            return salesforce_ids

        except Exception as e:
            raise osv.except_osv("Error Details!", e)

    def creating_orders(self, orders):
        try:
            salesforce_ids = []
            for order in orders:
                order_partner = self.env['res.partner'].search([('salesforce_id', '=', order['AccountId'])])
                if not order_partner:
                    query = "select id, name, shippingStreet," \
                            "ShippingCity,Website, " \
                            "ShippingPostalCode, shippingCountry, " \
                            "fax, phone, Description from account"

                    extend_query = " where id='" + order['AccountId'] + "'"
                    order_partner_new = self.sales_force.query(query + extend_query)["records"][0]
                    order_partner = self.env['res.partner'].create({
                        'salesforce_id': order_partner_new['Id'],
                        'location': 'SalesForce Order Account',
                        'name': order_partner_new['Name'],
                        'city': order_partner_new['ShippingCity'] if order_partner_new['ShippingCity'] else None,
                        'street': order_partner_new['ShippingStreet'] if order_partner_new['ShippingStreet'] else None,
                        'country_id': self.env['res.country'].search(
                            [('name', '=', order_partner_new['ShippingCountry'])]).id if
                        order_partner_new['ShippingCountry'] else None,
                        'zip': order_partner_new['ShippingPostalCode'] if order_partner_new[
                            'ShippingPostalCode'] else None,
                        'phone': order_partner_new['Phone'] if order_partner_new['Phone'] else None,
                        'is_company': True,
                    })
                    self.env.cr.commit()
                order_contract = self.env['sale.contract'].search([('salesforce_id', '=', order['ContractId'])])
                if not order_contract:
                    query = "select id, AccountId, status, startDate, contractTerm, contractNumber" \
                            " from contract"
                    extend_query = " where id='" + order['ContractId'] + "'"
                    contract = self.sales_force.query(query+extend_query)['records'][0]
                    if contract['AccountId']:
                        customer = self.env['res.partner'].search([('salesforce_id', '=', contract['AccountId'])])
                        if not customer:
                            query = "select id, name, shippingStreet," \
                                    "ShippingCity,Website, " \
                                    "ShippingPostalCode, shippingCountry, " \
                                    "fax, phone, Description from account"

                            extend_query = " where id='" + contract['AccountId'] + "'"
                            data = self.sales_force.query(query + extend_query)["records"][0]

                            customer = self.env['res.partner'].create({
                                'salesforce_id': data['Id'],
                                'name': data['Name'],
                                'location': 'SalesForce Order Account',
                                'city': data['ShippingCity'] if data['ShippingCity'] else None,
                                'street': data['ShippingStreet'] if data['ShippingStreet'] else None,
                                'zip': data['ShippingPostalCode'] if data['ShippingPostalCode'] else None,
                                'phone': data['Phone'] if data['Phone'] else None,
                                'is_company': True,
                                'customer': True,
                            })
                            self.env.cr.commit()

                        order_contract = self.env['sale.contract'].create({
                            'salesforce_id': contract['Id'],
                            'name': contract['ContractNumber'],
                            'location': 'SalesForce',
                            'customer_id': customer.id,
                            'sf_status': contract['Status'],
                            'start_date': contract['StartDate'],
                            'term_months': contract['ContractTerm'],
                        })
                        self.env.cr.commit()

                odoo_order = self.env['sale.order'].search([('salesforce_id_so', '=', order['Id'])])
                if not odoo_order:
                    odoo_order = self.env['sale.order'].create({
                        'salesforce_id_so': order['Id'],
                        "name": order["OrderNumber"],
                        "partner_id": order_partner.id,
                        "state": 'sale',
                        "sf_status_so": order['Status'],
                        "invoice_status": "no",
                        "date_order": order['EffectiveDate'],
                        'contract_id': order_contract.id,
                        'location': 'SalesForce',
                        'last_modified': order['LastModifiedDate'],
                    })
                    order_lines = self.sales_force.query("select Pricebookentry.Product2Id , listprice, Quantity from "
                                                         "orderitem where orderid='%s'" % str(order['Id']))["records"]
                    for order_line in order_lines:
                        product_id = order_line["PricebookEntry"]["Product2Id"]
                        order_product = self.env['product.template'].search([('salesforce_id', '=', product_id)])
                        if not order_product:
                            order_product_new = self.sales_force.query("SELECT Product2.Id, Product2.Name, "
                                                                       "Product2.ProductCode, Product2.Description,"
                                                                       " Product2.Family,UnitPrice from PriceBookEntry "
                                                                       "where Product2.Id='%s'" % str(product_id))[
                                "records"][0]
                            order_product = self.env['product.template'].create({
                                'salesforce_id': order_product_new['Product2']["Id"],
                                'name': order_product_new['Product2']["Name"],
                                'description': order_product_new['Product2']["Description"],
                                'default_code': order_product_new['Product2']["ProductCode"],
                                'list_price': order_product_new['UnitPrice'],
                                'invoice_policy': "delivery",
                            })

                            odoo_product = self.env['product.product'].search(
                                [('product_tmpl_id', '=', order_product.id)])
                            if not odoo_product:
                                self.env['product.product'].create({
                                    'product_tmpl_id': order_product.id
                                })
                                self.env.cr.commit()
                            else:
                                odoo_product.write({
                                    'product_tmpl_id': order_product.id
                                })

                        else:
                            odoo_product = self.env['product.product'].search([('product_tmpl_id',
                                                                                '=',
                                                                                order_product.id)])
                            if not odoo_product:
                                odoo_product = self.env['product.product'].create({
                                    'product_tmpl_id': order_product.id
                                })
                                self.env.cr.commit()

                        self.env['sale.order.line'].create({
                            'product_id': odoo_product[0].id,
                            'order_partner_id': order_partner.id,
                            "order_id": odoo_order.id,
                            "product_uom_qty": order_line['Quantity'],
                            'price_unit': order_line['ListPrice'],
                        })
                    self.env.cr.commit()
                elif odoo_order.last_modified != order['LastModifiedDate']:
                    odoo_order.write({
                        'salesforce_id_so': order['Id'],
                        "name": order["OrderNumber"],
                        "partner_id": order_partner.id,
                        "state": 'sale',
                        "sf_status_so": order['Status'],
                        "invoice_status": "no",
                        "date_order": order['EffectiveDate'],
                        'contract_id': order_contract.id,
                        'last_modified': order['LastModifiedDate'],
                    })
                    self.env.cr.commit()
                salesforce_ids.append(order['Id'])

            return salesforce_ids

        except Exception as e:
            raise osv.except_osv("Error Details!", e)

    def creating_products(self, products):
        try:
            salesforce_ids = []
            family = None
            for product in products:
                odoo_product = self.env['product.template'].search([('salesforce_id', '=', product['Product2']['Id'])])
                if product['Product2']['Family']:
                    family = self.env['product.family'].search([('name', '=', product['Product2']['Family'])])
                    if not family:
                        family = self.env['product.family'].create({
                            'name': product['Product2']['Family']
                        })
                        self.env.cr.commit()
                if not odoo_product:
                    new_product_template = self.env['product.template'].create({
                        'salesforce_id': product['Product2']['Id'],
                        'name': product['Product2']['Name'],
                        'description': product['Product2']['Description'],
                        'list_price': product['UnitPrice'] if product['UnitPrice'] else None,
                        'sf_product_family': family.id,
                        'location': 'SalesForce Product',
                        'default_code': product['Product2']['ProductCode'],
                        'last_modified': product['LastModifiedDate'],
                    })
                    product_product = self.env['product.product'].search(
                        [('product_tmpl_id', '=', new_product_template.id)])
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
                    odoo_product.write({
                        'salesforce_id': product['Product2']['Id'],
                        'name': product['Product2']['Name'],
                        'description': product['Product2']['Description'],
                        'list_price': product['UnitPrice'] if product['UnitPrice'] else None,
                        'sf_product_family': family.id,
                        'default_code': product['Product2']['ProductCode'],
                        'last_modified': product['LastModifiedDate'],
                    })
                    self.env.cr.commit()
                salesforce_ids.append(product['Product2']['Id'])

            return salesforce_ids

        except Exception as e:
            raise osv.except_osv("Error Details!", e)

    def creating_contacts(self, contacts):
        try:
            salesforce_ids = []
            parent = None
            for contact in contacts:
                if contact['AccountId']:
                    parent = self.env['res.partner'].search([('salesforce_id', '=', contact['AccountId'])])
                    if not parent:
                        query = "select id, name, shippingStreet," \
                                "ShippingCity,Website, " \
                                "ShippingPostalCode, shippingCountry, " \
                                "fax, phone, Description from account"

                        extend_query = " where id='" + contact['AccountId'] + "'"
                        parent_data = self.sales_force.query(query + extend_query)["records"][0]

                        parent = self.env['res.partner'].create({
                            'salesforce_id': parent_data['Id'],
                            'name': parent_data['Name'],
                            'city': parent_data['ShippingCity'] if parent_data['ShippingCity'] else None,
                            'street': parent_data['ShippingStreet'] if parent_data['ShippingStreet'] else None,
                            'zip': parent_data['ShippingPostalCode'] if parent_data['ShippingPostalCode'] else None,
                            'phone': parent_data['Phone'] if parent_data['Phone'] else None,
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
                if not child:
                    self.env['res.partner'].create({
                        'salesforce_id': contact['Id'],
                        'name': name,
                        'first_name': contact['FirstName'] if contact['FirstName'] else None,
                        'last_name': contact['LastName'] if contact['LastName'] else None,
                        'street': contact['OtherStreet'] if contact['OtherStreet'] else None,
                        'zip': contact['OtherPostalCode'] if contact['OtherPostalCode'] else None,
                        'phone': contact['Phone'] if contact['Phone'] else None,
                        'location': 'SalesForce Contact',
                        'is_company': False,
                        'parent_id': parent[0].id if parent else None,
                        'last_modified': contact['LastModifiedDate'],
                    })
                #     self.sales_force.Contact.updated(datetime.datetime.now(pytz.UTC) - datetime.timedelta(days=29),
                #     datetime.datetime.now(pytz.UTC))
                #     elif contact['CreatedDate'] > str(pytz.utc.localize(self.to_date) - datetime.timedelta(days=29)) and \
                #       contact['CreatedDate'] < str(pytz.utc.localize(self.to_date)) and contact['id'] ==
                #       child['salesforce_id']:

                # elif child['salesforce_id'] in updated_ids:
                elif child.last_modified != contact['LastModifiedDate']:
                    child.write({
                        'salesforce_id': contact['Id'],
                        'name': name,
                        'first_name': contact['FirstName'] if contact['FirstName'] else None,
                        'last_name': contact['LastName'] if contact['LastName'] else None,
                        'street': contact['OtherStreet'] if contact['OtherStreet'] else None,
                        'zip': contact['OtherPostalCode'] if contact['OtherPostalCode'] else None,
                        'phone': contact['Phone'] if contact['Phone'] else None,
                        'is_company': False,
                        'parent_id': parent[0].id if parent else None,
                    })
                self.env.cr.commit()
                salesforce_ids.append(contact['Id'])
            return salesforce_ids

        except Exception as e:
            raise osv.except_osv("Error Details!", e)

    def creating_contracts(self, contracts):
        try:
            salesforce_ids = []
            for contract in contracts:
                if contract['AccountId']:
                    customer = self.env['res.partner'].search([('salesforce_id', '=', contract['AccountId'])])
                    if not customer:
                        query = "select id, name, shippingStreet," \
                                "ShippingCity,Website, " \
                                "ShippingPostalCode, shippingCountry, " \
                                "fax, phone, Description from account"

                        extend_query = " where id='" + contract['AccountId'] + "'"
                        data = self.sales_force.query(query + extend_query)["records"][0]

                        customer = self.env['res.partner'].create({
                            'salesforce_id': data['Id'],
                            'name': data['Name'],
                            'location': 'SalesForce Contract Account',
                            'city': data['ShippingCity'] if data['ShippingCity'] else None,
                            'street': data['ShippingStreet'] if data['ShippingStreet'] else None,
                            'zip': data['ShippingPostalCode'] if data['ShippingPostalCode'] else None,
                            'phone': data['Phone'] if data['Phone'] else None,
                            'is_company': True,
                            # 'customer': True,
                        })
                        self.env.cr.commit()
                    odoo_contract = self.env['sale.contract'].search([('salesforce_id', '=', contract['Id'])])
                    if not odoo_contract:
                        self.env['sale.contract'].create({
                            'salesforce_id': contract['Id'],
                            'name': contract['ContractNumber'],
                            'customer_id': customer.id,
                            'sf_status': contract['Status'],
                            'start_date': contract['StartDate'],
                            'term_months': contract['ContractTerm'],
                            'location': 'SalesForce',
                            'last_modified': contract['LastModifiedDate'],
                        })
                    elif odoo_contract.last_modified != contract['LastModifiedDate']:
                        odoo_contract.write({
                            'salesforce_id': contract['Id'],
                            'name': contract['ContractNumber'],
                            'customer_id': customer.id,
                            'sf_status': contract['Status'],
                            'start_date': contract['StartDate'],
                            'term_months': contract['ContractTerm'],
                            'last_modified': contract['LastModifiedDate'],
                        })
                    self.env.cr.commit
                salesforce_ids.append(contract['Id'])

            return salesforce_ids

        except Exception as e:
            raise osv.except_osv("Error Details!", e)

    def creating_opportunities(self, opportunities):
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
                            query = "select id, name, shippingStreet," \
                                    "ShippingCity,Website, " \
                                    "ShippingPostalCode, shippingCountry, " \
                                    "fax, phone, Description from account"

                            extend_query = " where id='" + lead['AccountId'] + "'"
                            partner = self.sales_force.query(query + extend_query)["records"][0]
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
                        lead_stage = self.env['crm.stage'].search([('name', '=', lead['StageName'])])
                        if not lead_stage:
                            lead_stage = self.env['crm.stage'].create({
                                'name': lead['StageName'],
                            })

                        odoo_lead.write({
                            'salesforce_id': lead['Id'],
                            'name': lead['Name'],
                            'partner_id': lead_partner.id,
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

                        })
                        self.env.cr.commit()
                    else:
                        lead_stage = self.env['crm.stage'].search([('name', '=', lead['StageName'])])
                        if not lead_stage:
                            lead_stage = self.env['crm.stage'].create({
                                'name': lead['StageName'],
                            })

                        odoo_lead.write({
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
                        })
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
                            query = "select id, name, shippingStreet," \
                                    "ShippingCity,Website, " \
                                    "ShippingPostalCode, shippingCountry, " \
                                    "fax, phone, Description from account"

                            extend_query = " where id='" + lead['AccountId'] + "'"
                            partner = self.sales_force.query(query + extend_query)["records"][0]
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
                        lead_stage = self.env['crm.stage'].search([('name', '=', lead['StageName'])])
                        if not lead_stage:
                            lead_stage = self.env['crm.stage'].create({
                                'name': lead['StageName'],
                            })

                        self.env['crm.lead'].create({
                            'salesforce_id': lead['Id'],
                            'name': lead['Name'],
                            'location': 'SalesForce',
                            'partner_id': lead_partner.id,
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
                        })
                        self.env.cr.commit()
                    else:
                        lead_stage = self.env['crm.stage'].search([('name', '=', lead['StageName'])])
                        if not lead_stage:
                            lead_stage = self.env['crm.stage'].create({
                                'name': lead['StageName'],
                            })

                        self.env['crm.lead'].create({
                            'salesforce_id': lead['Id'],
                            'name': lead['Name'],
                            'location': 'SalesForce',
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
                        })
                        self.env.cr.commit()
                salesforce_ids.append(lead['Id'])

            return salesforce_ids

        except Exception as e:
            raise osv.except_osv("Error Details!", e)

    def creating_leads(self, leads):
        try:
            salesforce_ids = []
            source = None
            priority = None
            title = None

            for lead in leads:
                odoo_lead = self.env['crm.lead'].search([('salesforce_id', '=', lead['Id'])])
                if not odoo_lead:
                    if lead['LeadSource']:
                        source = self.env['utm.source'].search([('name', '=', lead['LeadSource'])])
                        if not source:
                            source = self.env['utm.source'].create({
                                'name': lead['LeadSource'],
                            })
                            self.env.cr.commit()
                    first_name = lead['FirstName'] if lead['FirstName'] else ""
                    last_name = lead['LastName'] if lead['LastName'] else ""
                    name = first_name + " " + last_name
                    if lead['Rating'] == 'Hot':
                        priority = '3'
                    elif lead['Rating'] == 'Warm':
                        priority = '2'
                    elif lead['Rating'] == 'Cold':
                        priority = '1'
                    else:
                        priority = None

                    if lead['Salutation']:
                        title = self.env['res.partner.title'].search([('name', '=', lead['Salutation'])])
                        if not title:
                            title = self.env['res.partner.title'].create({
                                'name': lead['Salutation'],
                            })

                    odoo_lead = self.env['crm.lead'].create({
                        'salesforce_id': lead['Id'],
                        'name': lead['Company'],
                        'contact_name': name,
                        'location': 'SalesForce',
                        'title': title.id if title else None,
                        'planned_revenue': lead['AnnualRevenue'] if lead['AnnualRevenue'] else None,
                        'type': 'lead',
                        'description': lead['Description'] if lead['Description'] else None,
                        'source_id': source.id if source else None,
                        'sf_industry': lead['Industry'] if lead['Industry'] else None,
                        'sf_title': lead['Title'] if lead['Title'] else None,
                        'sf_status': lead['Status'] if lead['Status'] else None,
                        'priority': priority,
                        'city': lead['City'] if lead['City'] else None,
                        'street': lead['Street'] if lead['Street'] else None,
                        'country_id': self.env['res.country'].search(
                            [('name', '=', lead['Country'])]).id if
                        lead['Country'] else None,
                        'zip': lead['PostalCode'] if lead['PostalCode'] else None,
                        'state_id': self.env['res.country.state'].search(
                            [('name', '=', lead['State'])]).id if
                        lead['State'] else None,
                        'phone': lead['Phone'] if lead['Phone'] else None,
                        'last_modified': lead['LastModifiedDate'],
                    })

                elif odoo_lead.last_modified != lead['LastModifiedDate']:
                    if lead['LeadSource']:
                        source = self.env['utm.source'].search([('name', '=', lead['LeadSource'])])
                        if not source:
                            source = self.env['utm.source'].create({
                                'name': lead['LeadSource'],
                            })
                            self.env.cr.commit()
                    first_name = lead['FirstName'] if lead['FirstName'] else ""
                    last_name = lead['LastName'] if lead['LastName'] else ""
                    name = first_name + " " + last_name
                    if lead['Rating'] == 'Hot':
                        priority = '3'
                    elif lead['Rating'] == 'Warm':
                        priority = '2'
                    elif lead['Rating'] == 'Cold':
                        priority = '1'
                    else:
                        priority = None

                    if lead['Salutation']:
                        title = self.env['res.partner.title'].search([('name', '=', lead['Salutation'])])
                        if not title:
                            title = self.env['res.partner.title'].create({
                                'name': lead['Salutation'],
                            })

                    odoo_lead.write({
                        'salesforce_id': lead['Id'],
                        'name': lead['Company'],
                        'contact_name': name,
                        'title': title.id if title else None,
                        'planned_revenue': lead['AnnualRevenue'] if lead['AnnualRevenue'] else None,
                        'type': 'lead',
                        'description': lead['Description'] if lead['Description'] else None,
                        'source_id': source.id if source else None,
                        'sf_industry': lead['Industry'] if lead['Industry'] else None,
                        'sf_title': lead['Title'] if lead['Title'] else None,
                        'sf_status': lead['Status'] if lead['Status'] else None,
                        'priority': priority,
                        'city': lead['City'] if lead['City'] else None,
                        'street': lead['Street'] if lead['Street'] else None,
                        'country_id': self.env['res.country'].search(
                            [('name', '=', lead['Country'])]).id if
                        lead['Country'] else None,
                        'zip': lead['PostalCode'] if lead['PostalCode'] else None,
                        'state_id': self.env['res.country.state'].search(
                            [('name', '=', lead['State'])]).id if
                        lead['State'] else None,
                        'phone': lead['Phone'] if lead['Phone'] else None,
                        'last_modified': lead['LastModifiedDate'],
                    })
                self.env.cr.commit()
                salesforce_ids.append(lead['Id'])

            return salesforce_ids

        except Exception as e:
            raise osv.except_osv("Error Details!", e)

    def creating_tasks(self, tasks):
        try:
            salesforce_ids = []
            user_title = None

            for task in tasks:
                partner_model = self.env['ir.model'].search([('model', '=', 'res.partner')])

                activity_type = self.env['mail.activity.type'].search([('name', '=', task['Subject'])])
                if not activity_type:
                    self.env['mail.activity.type'].create({
                        'name': task['Subject'],
                    })

                partner = self.env['res.partner'].search([('salesforce_id', '=', task['WhoId'])])
                if not partner:
                    query = "select id, name,email, OtherStreet,OtherCity," \
                            "OtherPostalCode, OtherCountry" \
                            ", phone, AccountId from Contact"
                    extend_query = " where id='" + task['WhoId'] + "'"
                    task_partner_new = self.sales_force.query(query + extend_query)["records"][0]

                    partner = self.env['res.partner'].create({
                        'salesforce_id': task_partner_new['Id'],
                        'name': task_partner_new['Name'],
                        'location': 'SalesForce Task Contact',
                        'city': task_partner_new['OtherCity'] if task_partner_new['OtherCity'] else None,
                        'street': task_partner_new['OtherStreet'] if task_partner_new['OtherStreet'] else None,
                        'country_id': self.env['res.country'].search(
                            [('name', '=', task_partner_new['OtherCountry'])]).id if
                        task_partner_new['OtherCountry'] else None,
                        'zip': task_partner_new['OtherPostalCode'] if task_partner_new[
                            'OtherPostalCode'] else None,
                        'phone': task_partner_new['Phone'] if task_partner_new['Phone'] else None,
                    })
                    self.env.cr.commit()

                query = "select id,name,title,email,phone,city,country,postalCode, state, street from User"
                extend_query = " where id='" + task['OwnerId'] + "'"
                task_user = self.sales_force.query(query + extend_query)["records"][0]
                user = self.env['res.users'].search(
                    ['|', ('salesforce_id', '=', task_user['Id']), ('email', '=', task_user['Email'])])
                if user:
                    user.write({
                        'salesforce_id': task_user['Id'],
                    })
                    self.env.cr.commit()
                if not user:
                    if task_user['Title']:
                        user_title = self.env['res.partner.title'].search([('name', '=', task_user['Title'])])
                        if not user_title:
                            user_title = self.env['res.partner.title'].create({
                                'name': task_user['Title']
                            })

                    user = self.env['res.users'].create({
                        'salesforce_id': task_user['Id'],
                        'name': task_user['Name'] if task_user['Name'] else None,
                        'login': task_user['Email'] if task_user['Email'] else None,
                        'phone': task_user['Phone'] if task_user['Phone'] else None,
                        'email': task_user['Email'] if task_user['Email'] else None,
                        'city': task_user['City'] if task_user['City'] else None,
                        'street': task_user['Street'] if task_user['Street'] else None,
                        'zip': task_user['PostalCode'] if task_user['PostalCode'] else None,
                        'state_id': self.env['res.country.state'].search(
                            [('name', '=', task_user['State'])]).id if
                        task_user['State'] else None,
                        'country_id': self.env['res.country'].search(
                            [('name', '=', task_user['Country'])]).id if
                        task_user['Country'] else None,
                        'title': user_title.id if user_title else None,
                    })

                odoo_task = self.env['mail.activity'].search([('salesforce_id', '=', task['Id'])])
                if not odoo_task:
                    self.env['mail.activity'].create({
                        'salesforce_id': task['Id'],
                        'res_id': partner.id,
                        'activity_type_id': activity_type.id,
                        'summary': task['Description'] if task['Description'] else None,
                        'date_deadline': task['ActivityDate'] if task['ActivityDate'] else None,
                        'note': task['Description'] if task['Description'] else None,
                        'res_model_id': partner_model.id,
                        'user_id': user.id,
                        'sf_priority': task['Priority'] if task['Priority'] else None,
                        'sf_status': task['Status'] if task['Status'] else None,
                        'last_modified': task['LastModifiedDate'],
                    })
                elif odoo_task.last_modified != task['LastModifiedDate']:
                    odoo_task.write({
                        'salesforce_id': task['Id'],
                        'res_id': partner.id,
                        'activity_type_id': activity_type.id,
                        'summary': task['Description'] if task['Description'] else None,
                        'date_deadline': task['ActivityDate'] if task['ActivityDate'] else None,
                        'note': task['Description'] if task['Description'] else None,
                        'res_model_id': partner_model.id,
                        'user_id': user.id,
                        'sf_priority': task['Priority'] if task['Priority'] else None,
                        'sf_status': task['Status'] if task['Status'] else None,
                        'last_modified': task['LastModifiedDate'],
                    })
                self.env.cr.commit()
                salesforce_ids.append(task['Id'])

            return salesforce_ids

        except Exception as e:
            raise osv.except_osv("Error Details!", e)

    def creating_calendars(self, calendars):
        try:
            salesforce_ids = []
            partner_ids = []
            attendee_ids = []
            partner = None
            user_title = None

            for calendar in calendars:
                if calendar['WhoId']:
                    partner = self.env['res.partner'].search([('salesforce_id', '=', calendar['WhoId'])])
                    if not partner:
                        query = "select id, name,email, OtherStreet,OtherCity, \
                                                            OtherPostalCode, OtherCountry, \
                                                            fax, phone, AccountId from Contact"

                        extend_query = " where id='" + calendar['WhoId'] + "'"
                        partner = self.sales_force.query(query + extend_query)["records"][0]
                        partner = self.env['res.partner'].create({
                            'salesforce_id': partner['Id'],
                            'name': partner['Name'],
                            'location': 'SaleForce Event Contact',
                            'city': partner['OtherCity'] if partner['OtherCity'] else None,
                            'street': partner['OtherStreet'] if partner['OtherStreet'] else None,
                            'zip': partner['OtherPostalCode'] if partner['OtherPostalCode'] else None,
                            'phone': partner['Phone'] if partner['Phone'] else None,
                        })

                    partner_ids.append(partner.id)

                query = "select id,name,title,email,phone,city,country,postalCode, state, street from User"
                extend_query = " where id='" + calendar['OwnerId'] + "'"
                calendar_user = self.sales_force.query(query + extend_query)["records"][0]
                user = self.env['res.users'].search([('email', '=', calendar_user['Email'])])
                if user:
                    user.write({
                        'salesforce_id': calendar_user['Id'],
                    })
                    self.env.cr.commit()

                if not user:
                    if calendar_user['Title']:
                        user_title = self.env['res.partner.title'].search([('name', '=', calendar_user['Title'])])
                        if not user_title:
                            user_title = self.env['res.partner.title'].create({
                                'name': calendar_user['Title']
                            })
                    user = self.env['res.users'].create({
                        'salesforce_id': calendar_user['Id'],
                        'name': calendar_user['Name'] if calendar_user['Name'] else None,
                        'login': calendar_user['Email'] if calendar_user['Email'] else None,
                        'phone': calendar_user['Phone'] if calendar_user['Phone'] else None,
                        'email': calendar_user['Email'] if calendar_user['Email'] else None,
                        'city': calendar_user['City'] if calendar_user['City'] else None,
                        'street': calendar_user['Street'] if calendar_user['Street'] else None,
                        'zip': calendar_user['PostalCode'] if calendar_user['PostalCode'] else None,
                        'state_id': self.env['res.country.state'].search(
                            [('name', '=', calendar_user['State'])]).id if
                        calendar_user['State'] else None,
                        'title': user_title.id if user_title else None,
                    })

                partner_ids.append(user.partner_id.id)

                odoo_calendar = self.env['calendar.event'].search([('salesforce_id', '=', calendar['Id'])])
                if not odoo_calendar:
                    self.env['calendar.event'].create({
                        'salesforce_id': calendar['Id'],
                        'name': calendar['Subject'],
                        'sf_location': 'SaleForce',
                        'partner_ids': [[6, 0, partner_ids]] if partner_ids else None,
                        'start': datetime.datetime.strptime(calendar['StartDateTime'][:-9], '%Y-%m-%dT%H:%M:%S'),
                        'stop': datetime.datetime.strptime(calendar['EndDateTime'][:-9], '%Y-%m-%dT%H:%M:%S'),
                        'description': calendar['Description'] if calendar['Description'] else None,
                        'allday': calendar['IsAllDayEvent'],
                        'location': calendar['Location'] if calendar['Location'] else None,
                        'last_modified': calendar['LastModifiedDate'],
                    })
                elif odoo_calendar.last_modified != calendar['LastModifiedDate']:
                    odoo_calendar.write({
                        'salesforce_id': calendar['Id'],
                        'name': calendar['Subject'],
                        'partner_ids': [[6, 0, partner_ids]] if partner_ids else None,
                        'start': datetime.datetime.strptime(calendar['StartDateTime'][:-9], '%Y-%m-%dT%H:%M:%S'),
                        'stop': datetime.datetime.strptime(calendar['EndDateTime'][:-9], '%Y-%m-%dT%H:%M:%S'),
                        'description': calendar['Description'] if calendar['Description'] else None,
                        'allday': calendar['IsAllDayEvent'],
                        'location': calendar['Location'] if calendar['Location'] else None,
                        'last_modified': calendar['LastModifiedDate'],
                    })

                if partner_ids:
                    for partner in partner_ids:
                        event_attendee = self.env['calendar.attendee'].search([('partner_id', '=', partner)])[0]
                        if not event_attendee:
                            event_attendee = self.env['calendar.attendee'].create({
                                'partner_id': partner.id,
                                'event_id': odoo_calendar.id,
                            })
                        attendee_ids.append(event_attendee.id)
                odoo_calendar.write({
                    'attendee_ids': [[6, 0, attendee_ids]] if attendee_ids else None,
                })
                self.env.cr.commit()
                salesforce_ids.append(calendar['Id'])

            return salesforce_ids

        except Exception as e:
            raise osv.except_osv("Error Details!", e)

    def export_opportunities_data(self, Auto):
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
            if username and password and security and enabler == 'True':
                sf = Salesforce(username=username, password=password, security_token=security)
                if not Auto:
                    crm_data = self.env['crm.lead'].search([('type', '=', 'opportunity')])
                else:
                    today = datetime.date.today()
                    yesterday = today - datetime.timedelta(days=1)
                    crm_data = self.env['crm.lead'].search([('type', '=', 'opportunity'), ('create_date', '>', yesterday),
                                                            ('create_date', '<', today)])
                exported_ids = []
                for opportunity in crm_data:
                    if opportunity.salesforce_id:
                        if len(sf.quick_search(opportunity.salesforce_id)) > 0:
                            date = str(datetime.datetime.now())
                            date_new, time = date.split(" ")
                            data = {
                                'Name': opportunity.name,
                                'AccountId': opportunity.partner_id.salesforce_id if opportunity.partner_id.salesforce_id else None,
                                'Amount': opportunity.planned_revenue if opportunity.planned_revenue else None,
                                'CloseDate': str(opportunity.date_closed).split(" ")[0] if opportunity.date_closed else date_new,
                                'Description': opportunity.description if opportunity.description else None,
                                'Probability': opportunity.probability if opportunity.probability else None,
                                'StageName': opportunity.stage_id.name if opportunity.stage_id else None,
                                'Type': opportunity.sf_type if opportunity.sf_type else None,
                                'CampaignId': opportunity.campaign_id.salesforce_id if opportunity.campaign_id.salesforce_id else None,
                                'LeadSource': opportunity.source_id.name if opportunity.source_id else None,
                            }
                            sf.Opportunity.update(opportunity.salesforce_id, data)
                    else:
                        date = str(datetime.datetime.now())
                        date_new, time = date.split(" ")
                        data = {
                            'Name': opportunity.name,
                            'AccountId': opportunity.partner_id.salesforce_id if opportunity.partner_id.salesforce_id else None,
                            'Amount': opportunity.planned_revenue if opportunity.planned_revenue else None,
                            'CloseDate': str(opportunity.date_closed).split(" ")[0] if opportunity.date_closed else date_new,
                            'Description': opportunity.description if opportunity.description else None,
                            'Probability': opportunity.probability if opportunity.probability else None,
                            'StageName': opportunity.stage_id.name if opportunity.stage_id else None,
                            'Type': opportunity.sf_type if opportunity.sf_type else None,
                            'CampaignId': opportunity.campaign_id.salesforce_id if opportunity.campaign_id.salesforce_id else None,
                            'LeadSource': opportunity.source_id.name if opportunity.source_id else None,
                        }
                        new_opportunity = sf.Opportunity.create(data)

                        opportunity.write({
                            'salesforce_id': new_opportunity['id']
                        })
                        self.env.cr.commit()
                    exported_ids.append(opportunity.id)

                return exported_ids

        except Exception as e:
            raise Warning(_(str(e)))

    def export_leads_data(self, Auto):
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
            if username and password and security and enabler == 'True':
                sf = Salesforce(username=username, password=password, security_token=security)
                if not Auto:
                    crm_data = self.env['crm.lead'].search([('type', '!=', 'opportunity')])
                else:
                    today = datetime.date.today()
                    yesterday = today - datetime.timedelta(days=1)
                    crm_data = self.env['crm.lead'].search([('type', '!=', 'opportunity'), ('create_date', '>', yesterday),
                                                            ('create_date', '<', today)])

                exported_ids = []
                for opportunity in crm_data:
                    if opportunity.salesforce_id:
                        if len(sf.quick_search(opportunity.salesforce_id)) > 0:
                            if opportunity.priority == '3':
                                priority = 'Hot'
                            elif opportunity.priority == '2':
                                priority = 'Warm'
                            elif opportunity.priority == '1':
                                priority = 'Cold'
                            else:
                                priority = None
                            data = {
                                'Salutation': opportunity.title.name if opportunity.title else None,
                                'LastName': opportunity.contact_name if opportunity.contact_name else self.name,
                                'Phone': opportunity.partner_id.phone if opportunity.partner_id.phone else None,
                                'Company': opportunity.name if opportunity.name else None,
                                'Email': opportunity.email_from if opportunity.email_from else None,
                                'Industry': opportunity.sf_industry if opportunity.sf_industry else None,
                                'Status': opportunity.sf_status if opportunity.sf_status else None,
                                'AnnualRevenue': opportunity.planned_revenue if opportunity.planned_revenue else None,
                                'Description': opportunity.description if opportunity.description else None,
                                'LeadSource': opportunity.source_id.name if opportunity.source_id else None,
                                'Rating': priority,
                                'City': opportunity.city if opportunity.city else None,
                                'Country': opportunity.country_id.name if opportunity.country_id else None,
                                'PostalCode': opportunity.zip if opportunity.zip else None,
                                'State': opportunity.state_id.name if opportunity.state_id else None,
                                'Street': opportunity.street if opportunity.street else None,
                                'Title': opportunity.sf_title if opportunity.sf_title else None,
                            }
                            sf.Lead.update(opportunity.salesforce_id, data)
                    else:
                        if opportunity.priority == '3':
                            priority = 'Hot'
                        elif opportunity.priority == '2':
                            priority = 'Warm'
                        elif opportunity.priority == '1':
                            priority = 'Cold'
                        else:
                            priority = None
                        data = {
                            'Salutation': opportunity.title.name if opportunity.title else None,
                            'LastName': opportunity.contact_name if opportunity.contact_name else self.name,
                            'Phone': opportunity.partner_id.phone if opportunity.partner_id.phone else None,
                            'Company': opportunity.name if opportunity.name else None,
                            'Email': opportunity.email_from if opportunity.email_from else None,
                            'Industry': opportunity.sf_industry if opportunity.sf_industry else None,
                            'Status': opportunity.sf_status if opportunity.sf_status else None,
                            'AnnualRevenue': opportunity.planned_revenue if opportunity.planned_revenue else None,
                            'Description': opportunity.description if opportunity.description else None,
                            'LeadSource': opportunity.source_id.name if opportunity.source_id else None,
                            'Rating': priority,
                            'City': opportunity.city if opportunity.city else None,
                            'Country': opportunity.country_id.name if opportunity.country_id else None,
                            'PostalCode': opportunity.zip if opportunity.zip else None,
                            'State': opportunity.state_id.name if opportunity.state_id else None,
                            'Street': opportunity.street if opportunity.street else None,
                            'Title': opportunity.sf_title if opportunity.sf_title else None,
                        }
                        new_opportunity = sf.Lead.create(data)
                        opportunity.write({
                            'salesforce_id': new_opportunity['id']
                        })
                        self.env.cr.commit()
                    exported_ids.append(opportunity.id)

                return exported_ids

        except Exception as e:
            raise Warning(_(str(e)))

    def export_sales_orders_data(self, Auto):
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
            if username and password and security and enabler == 'True':
                sf = Salesforce(username=username, password=password, security_token=security)
                if not Auto:
                    orders = self.env['sale.order'].search([('state', '=', 'sale')])
                else:
                    today = datetime.date.today()
                    yesterday = today - datetime.timedelta(days=1)
                    orders = self.env['sale.order'].search([('state', '=', 'sale'), ('create_date', '>', yesterday),
                                                            ('create_date', '<', today)])
                exported_ids = []
                for order in orders:
                    if order.salesforce_id_so:
                        if len(sf.quick_search(order.salesforce_id_so)) > 0:
                            data = {
                                'Status': order.sf_status_qo,
                            }
                            sf.Order.update(order.salesforce_id_so, data)
                    else:
                        if order.partner_id.salesforce_id:
                            Account_Id = order.partner_id.salesforce_id
                        else:
                            data = {
                                'Name': order.partner_id.name if order.partner_id.name else None,
                                'ShippingCity': order.partner_id.city if order.partner_id.city else None,
                                'ShippingStreet': order.partner_id.street if order.partner_id.street else None,
                                'ShippingCountry': self.env['res.country'].search(
                                    [('id', '=',
                                      order.partner_id.country_id.id)]).name if order.partner_id.country_id else None,
                                'ShippingPostalCode': order.partner_id.zip if order.partner_id.zip else None,
                                'Phone': order.partnnew_quoteer_id.phone if order.partner_id.phone else None,
                            }
                            new_account = sf.Account.create(data)
                            order.partner_id.write({
                                'salesforce_id': new_account['Id']
                            })
                            self.env.cr.commit()
                            Account_Id = new_account['Id']
                        if order.contract_id.salesforce_id:
                            Contract_Id = order.contract_id.salesforce_id
                        else:
                            data = {
                                'AccountId': Account_Id,
                                'Status': order.contract_id.sf_status if order.contract_id.sf_status else None,
                                'ContractTerm': order.contract_id.term_months if order.contract_id.term_months else None,
                                'OwnerId': self.env.user.salesforce_id if self.env.user.salesforce_id else None,
                                'StartDate': str(order.contract_id.start_date).split(" ")[0] if order.contract_id.start_date else None,
                            }
                            new_contract = sf.Contract.create(data)
                            order.contract_id.write({
                                'salesforce_id': new_contract['id'],
                            })
                            self.env.cr.commit()
                            Contract_Id = new_contract['id']
                        pricebook2 = sf.query("SELECT id from Pricebook2")["records"][0]

                        data = {
                            'ContractId': Contract_Id,
                            'AccountId': Account_Id,
                            'Pricebook2Id': pricebook2['Id'],
                            'EffectiveDate': str(order.date_order).split(" ")[0],
                            'Status': order.sf_status_so,
                            # 'QuoteId': order.salesforce_id_qo
                        }
                        new_order = sf.Order.create(data)

                        if order.order_line:
                            products = order.order_line
                            for product in products:
                                if not product.product_template_id.salesforce_id:
                                    data = {
                                        'Name': product.name,
                                        'Description': product.description if product.description else None,
                                        'ProductCode': product.default_code if product.default_code else None,
                                    }
                                    new_product = sf.Product2.create(data)
                                    product.write({
                                        'salesforce_id': new_product['id']
                                    })
                                    self.env.cr.commit()

                                pricebookentry = sf.query("SELECT id, Product2.Id from PriceBookEntry where Product2.Id='%s'" % str(product.product_template_id.salesforce_id))["records"][0]

                                data = {
                                    'Product2Id': pricebookentry['Product2']['Id'],
                                    'PricebookEntryId': pricebookentry['Id'],
                                    'UnitPrice': product.price_unit,
                                    'Quantity': product.product_uom_qty,
                                    'OrderId': new_order['id']
                                }
                                new_order_line = sf.OrderItem.create(data)
                        order.write({
                            'salesforce_id_so': new_order['id']
                        })
                        self.env.cr.commit()
                    exported_ids.append(order.id)

                return exported_ids
        except Exception as e:
            raise Warning(_(str(e)))

    def export_quotes_data(self, Auto):
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
            if username and password and security and enabler == 'True':
                sf = Salesforce(username=username, password=password, security_token=security)
                if not Auto:
                    orders = self.env['sale.order'].search([('state', '=', 'draft')])
                else:
                    today = datetime.date.today()
                    yesterday = today - datetime.timedelta(days=1)
                    orders = self.env['sale.order'].search([('state', '=', 'draft'), ('create_date', '>', yesterday),
                                                            ('create_date', '<', today)])

                exported_ids = []
                for order in orders:
                    if order.salesforce_id_qo:
                        if len(sf.quick_search(order.salesforce_id_qo)) > 0:
                            data = {
                                'Status': order.sf_status_qo,
                            }
                            sf.Quote.update(order.salesforce_id_qo, data)
                    else:
                        pricebook2 = sf.query("SELECT id from Pricebook2")["records"][0]
                        data = {
                            'Name': order.sf_name,
                            'OpportunityId': order.opportunity_id.salesforce_id,
                            'Pricebook2Id': pricebook2['Id'],
                            'ExpirationDate': str(order.date_order).split(" ")[0],
                            'Status': order.sf_status_qo,
                        }
                        new_quote = sf.Quote.create(data)

                        if order.order_line:
                            products = order.order_line
                            for product in products:
                                if not product.product_template_id.salesforce_id:
                                    data = {
                                        'Name': product.name,
                                        'Description': product.description if product.description else None,
                                        'ProductCode': product.default_code if product.default_code else None,
                                    }
                                    new_product = sf.Product2.create(data)
                                    product.product_template_id.write({
                                        'salesforce_id': new_product['id']
                                    })
                                    self.env.cr.commit()
                                pricebookentry = sf.query(
                                    "SELECT id, Product2.Id from PriceBookEntry where Product2.Id='%s'" % str(
                                        product.product_template_id.salesforce_id))["records"][0]

                                data = {
                                    'Product2Id': pricebookentry['Product2']['Id'],
                                    'PricebookEntryId': pricebookentry['Id'],
                                    'UnitPrice': product.price_unit,
                                    'Quantity': product.product_uom_qty,
                                    'QuoteId': new_quote['id']
                                }
                                new_quote_line = sf.QuoteLineItem.create(data)
                        order.write({
                            'salesforce_id_qo': new_quote['id']
                        })
                        self.env.cr.commit()

                    exported_ids.append(order.id)

                return exported_ids
        except Exception as e:
            raise Warning(_(str(e)))

    def export_products_data(self, Auto):
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
            if username and password and security and enabler == 'True':
                sf = Salesforce(username=username, password=password, security_token=security)
                if not Auto:
                    products = self.env['product.template'].search([])
                else:
                    today = datetime.date.today()
                    yesterday = today - datetime.timedelta(days=1)
                    products = self.env['product.template'].search([('create_date', '>', yesterday), ('create_date', '<', today)])
                exported_ids = []
                for product in products:
                    if product.salesforce_id:
                        if len(sf.quick_search(product.salesforce_id)) > 0:
                            data = {
                                'Name': product.name,
                                'Description': product.description if product.description else None,
                                'ProductCode': product.default_code if product.default_code else None,
                            }
                            sf.Product2.update(product.salesforce_id, data)
                    else:
                        data = {
                            'Name': product.name,
                            'Description': product.description if product.description else None,
                            'ProductCode': product.default_code if product.default_code else None,
                        }
                        new_contact = sf.Product2.create(data)
                        product.write({
                            'salesforce_id': new_contact['id']
                        })
                        self.env.cr.commit()

                    exported_ids.append(product.id)
                return exported_ids

        except Exception as e:
            raise Warning(_(str(e)))

    def export_customers_data(self, Auto):
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')

            if username and password and security and enabler == 'True':
                sf = Salesforce(username=username, password=password, security_token=security)
                if not Auto:
                    contacts = self.env['res.partner'].search([('user_ids', '=', False)])
                else:
                    today = datetime.date.today()
                    yesterday = today - datetime.timedelta(days=1)
                    contacts = self.env['res.partner'].search([('user_ids','=', False), ('create_date', '>', yesterday), ('create_date', '<', today)])
                exported_ids = []
                for contact in contacts:
                    if contact.salesforce_id:
                        if len(sf.quick_search(contact.salesforce_id)) > 0:
                            if contact.customer_rank == 0:
                                data = {
                                    'FirstName': contact.first_name if contact.first_name else None,
                                    'LastName': contact.last_name if contact.last_name else None,
                                    'Email': contact.email if contact.email else None,
                                    'OtherCity': contact.city if contact.city else None,
                                    'OtherStreet': contact.street if contact.street else None,
                                    'OtherCountry': self.env['res.country'].search(
                                        [('id', '=', contact.country_id.id)]).name if contact.country_id else None,
                                    'OtherPostalCode': contact.zip if contact.zip else None,
                                    'Phone': contact.phone if contact.phone else None,
                                    'AccountId': contact.parent_id.salesforce_id if contact.parent_id.salesforce_id else None,
                                }
                                sf.Contact.update(contact.salesforce_id, data)
                            else:
                                data = {
                                    'Name': contact.name if contact.name else None,
                                    'ShippingCity': contact.city if contact.city else None,
                                    'ShippingStreet': contact.street if contact.street else None,
                                    'ShippingCountry': self.env['res.country'].search(
                                        [('id', '=', contact.country_id.id)]).name if contact.country_id else None,
                                    'ShippingPostalCode': contact.zip if contact.zip else None,
                                    'Phone': contact.phone if contact.phone else None,
                                }
                                sf.Account.update(contact.salesforce_id, data)
                    else:
                        if contact.customer_rank == 0:
                            data = {
                                'FirstName': contact.first_name if contact.first_name else None,
                                'LastName': contact.last_name if contact.last_name else None,
                                'Email': contact.email if contact.email else None,
                                'OtherCity': contact.city if contact.city else None,
                                'OtherStreet': contact.street if contact.street else None,
                                'OtherCountry': self.env['res.country'].search(
                                    [('id', '=', contact.country_id.id)]).name if contact.country_id else None,
                                'OtherPostalCode': contact.zip if contact.zip else None,
                                'Phone': contact.phone if contact.phone else None,
                                'AccountId': contact.parent_id.salesforce_id if contact.parent_id.salesforce_id else None,
                            }
                            new_contact = sf.Contact.create(data)
                        else:
                            data = {
                                'Name': contact.name if contact.name else None,
                                'ShippingCity': contact.city if contact.city else None,
                                'ShippingStreet': contact.street if contact.street else None,
                                'ShippingCountry': self.env['res.country'].search(
                                    [('id', '=', contact.country_id.id)]).name if contact.country_id else None,
                                'ShippingPostalCode': contact.zip if contact.zip else None,
                                'Phone': contact.phone if contact.phone else None,
                            }
                            new_contact = sf.Account.create(data)
                        contact.write({
                            'salesforce_id': new_contact['id']
                        })
                        self.env.cr.commit()
                    exported_ids.append(contact.id)

                return exported_ids

        except Exception as e:
            raise Warning(_(str(e)))


class SyncHistory(models.Model):
    _name = 'sync.history'
    _order = 'sync_date desc'

    field_name = fields.Char('sync_history')
    sync_id = fields.Many2one('salesforce.connector', string='Partner Reference', required=True, ondelete='cascade',
                              index=True, copy=False)
    sync_date = fields.Datetime(_('Sync Date'), readonly=True, required=True, default=fields.Datetime.now)
    no_of_orders_sync = fields.Integer(_('SalesOrders'), readonly=True)
    no_of_products_sync = fields.Integer(_('Products'), readonly=True)
    no_of_customers_sync = fields.Integer(_('Customers'), readonly=True)
    no_of_opportunities_sync = fields.Integer(_('Opportunities'), readonly=True)
    no_of_leads_sync = fields.Integer(_('Leads'), readonly=True)
    no_of_tasks_sync = fields.Integer(_('Tasks'), readonly=True)
    no_of_calendars_sync = fields.Integer(_('Calendars'), readonly=True)
    no_of_quotes_sync = fields.Integer(_('Quotes'), readonly=True)
    no_of_contracts_sync = fields.Integer(_('Contracts'), readonly=True)
    sync_nature = fields.Char(_('Type'), readonly=True)
    document_link = fields.Char(_('Document Link'), readonly=True)

    def sync_data(self):
        client_action = {
            'type': 'ir.actions.act_url',
            'name': "log_file",
            'target': 'new',
            'url': self.document_link
        }
        return client_action