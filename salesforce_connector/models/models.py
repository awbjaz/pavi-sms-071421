# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, exceptions, _
from simple_salesforce import Salesforce
from openerp import _
from openerp.exceptions import Warning, ValidationError
from odoo.osv import osv
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class SalesForceSettingModel(models.TransientModel):
    _inherit = 'res.config.settings'

    sf_username = fields.Char(string='Username')
    sf_password = fields.Char(string='Password')
    sf_security_token = fields.Char(string='Security Token')
    sf_salesforce_enable = fields.Boolean(string="Salesforce Setting Enabler", default=False)
    sf_lead = fields.Boolean(string="Leads", default=False)
    sf_opportunity = fields.Boolean(string="Opportunities", default=False)
    sf_account = fields.Boolean(string="Accounts", default=False)
    sf_contact = fields.Boolean(string="Contacts", default=False)
    sf_saleorder = fields.Boolean(string="Orders", default=False)
    sf_product = fields.Boolean(string="Products", default=False)
    sf_event = fields.Boolean(string="Events", default=False)
    sf_task = fields.Boolean(string="Tasks", default=False)
    sf_contract = fields.Boolean(string="Contracts", default=False)
    sf_quote = fields.Boolean(string="Quotes", default=False)

    def get_log(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Salesforce Logs',
            'view_mode': 'tree',
            'res_model': 'sync.history',
            'context': "{'create': False}"
        }

    def set_values(self):
        res = super(SalesForceSettingModel, self).set_values()
        self.env['ir.config_parameter'].set_param('odoo_salesforce.sf_username', self.sf_username)
        self.env['ir.config_parameter'].set_param('odoo_salesforce.sf_password', self.sf_password)
        self.env['ir.config_parameter'].set_param('odoo_salesforce.sf_security_token', self.sf_security_token)
        self.env['ir.config_parameter'].set_param('odoo_salesforce.sf_salesforce_enable', self.sf_salesforce_enable)
        self.env['ir.config_parameter'].set_param('odoo_salesforce.sf_contact', self.sf_contact)
        self.env['ir.config_parameter'].set_param('odoo_salesforce.sf_product', self.sf_product)
        self.env['ir.config_parameter'].set_param('odoo_salesforce.sf_opportunity', self.sf_opportunity)
        self.env['ir.config_parameter'].set_param('odoo_salesforce.sf_lead', self.sf_lead)
        self.env['ir.config_parameter'].set_param('odoo_salesforce.sf_task', self.sf_task)
        self.env['ir.config_parameter'].set_param('odoo_salesforce.sf_event', self.sf_event)
        self.env['ir.config_parameter'].set_param('odoo_salesforce.sf_account', self.sf_account)
        self.env['ir.config_parameter'].set_param('odoo_salesforce.sf_saleorder', self.sf_saleorder)
        self.env['ir.config_parameter'].set_param('odoo_salesforce.sf_contract', self.sf_contract)
        self.env['ir.config_parameter'].set_param('odoo_salesforce.sf_quote', self.sf_quote)

        return res

    @api.model
    def get_values(self):
        res = super(SalesForceSettingModel, self).get_values()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
        password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
        security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
        enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
        contact = IrConfigParameter.get_param('odoo_salesforce.sf_contact')
        product = IrConfigParameter.get_param('odoo_salesforce.sf_product')
        opportunity = IrConfigParameter.get_param('odoo_salesforce.sf_opportunity')
        lead = IrConfigParameter.get_param('odoo_salesforce.sf_lead')
        task = IrConfigParameter.get_param('odoo_salesforce.sf_task')
        event = IrConfigParameter.get_param('odoo_salesforce.sf_event')
        account = IrConfigParameter.get_param('odoo_salesforce.sf_account')
        order = IrConfigParameter.get_param('odoo_salesforce.sf_saleorder')
        contract = IrConfigParameter.get_param('odoo_salesforce.sf_contract')
        quote = IrConfigParameter.get_param('odoo_salesforce.sf_quote')

        res.update(
            sf_username=username,
            sf_password=password,
            sf_security_token=security,
            sf_salesforce_enable=True if enabler == 'True' else False,
            sf_contact=True if contact == 'True' else False,
            sf_product=True if product == 'True' else False,
            sf_opportunity=True if opportunity == 'True' else False,
            sf_lead=True if lead == 'True' else False,
            sf_task=True if task == 'True' else False,
            sf_event=True if event == 'True' else False,
            sf_account=True if account == 'True' else False,
            sf_saleorder=True if order == 'True' else False,
            sf_contract=True if contract == 'True' else False,
            sf_quote=True if quote == 'True' else False
        )

        return res

    def test_credentials(self):
        """
        Tests the user SalesForce account credentials

        :return:
        """
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            sf = Salesforce(username=username, password=password, security_token=security)
            query = "select id,name,title,email,phone,city,country,postalCode, state, street from User"
            extend_query = " where email='" + self.env.user.email + "'"
            user = sf.query(query + extend_query)["records"][0]
            user = sf.query(query + extend_query)["records"][0]
            odoo_user = self.env['res.users'].search([('email', '=', user['Email'])])
            if odoo_user:
                odoo_user.write({
                    'salesforce_id': user['Id'],
                })
                self.env.cr.commit()

            if not odoo_user:
                if user['Title']:
                    user_title = self.env['res.partner.title'].search([('name', '=', user['Title'])])
                    if not user_title:
                        user_title = self.env['res.partner.title'].create({
                            'name': user['Title']
                        })
                user = self.env['res.users'].create({
                    'salesforce_id': user['Id'],
                    'name': user['Name'] if user['Name'] else None,
                    'login': user['Email'] if user['Email'] else None,
                    'phone': user['Phone'] if user['Phone'] else None,
                    'email': user['Email'] if user['Email'] else None,
                    'city': user['City'] if user['City'] else None,
                    'street': user['Street'] if user['Street'] else None,
                    'zip': user['PostalCode'] if user['PostalCode'] else None,
                    'state_id': self.env['res.country.state'].search(
                        [('name', '=', user['State'])]).id if
                    user['State'] else None,
                    'title': user_title.id if user_title else None,
                })


        except Exception as e:
            raise Warning(_(str(e)))

        raise osv.except_osv(_("Success!"), (_("Credentials are successfully tested.")))


class CustomPartner(models.Model):
    _inherit = "res.partner"

    salesforce_id = fields.Char(string="SalesForce Id")
    export_contact = fields.Boolean(_('Export To Salesforce'))
    # sf_customer_name = fields.Char(string=_("SalesForce Customer Name"), readonly=True)
    first_name = fields.Char(string="SalesForce First Name")
    last_name = fields.Char(string="Salesforce Last Name")
    last_modified = fields.Char(string='Last Modified Date')
    location = fields.Char(string='Location')
    contract_counter = fields.Integer(string='Contract', compute='contract_counters')

    def contract_counters(self):
        self.contract_counter = self.env['sale.contract'].search_count([('customer_id', '=', self.id)])
        print('xyz')

    def get_contracts(self):
        return {
            'name': (_('SalesForce Contracts')),
            # 'domains': [('contact_ids','=', self.display_name)],
            'domain': [('customer_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'sale.contract',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def unlink(self):
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
            contact_d = IrConfigParameter.get_param('odoo_salesforce.sf_contact')
            account_d = IrConfigParameter.get_param('odoo_salesforce.sf_account')
            if username and password and security and enabler == 'True' and (contact_d == 'True' or account_d == 'True'):
                sf = Salesforce(username=username, password=password, security_token=security)
                for contact in self:
                    if contact.salesforce_id and contact.customer_rank == 0 and contact_d == 'True':
                        # if len(sf.quick_search(contact.salesforce_id)['searchRecords']) > 0:
                        try:
                            sf.Contact.delete(contact.salesforce_id)
                        except:
                            continue
                    elif contact.salesforce_id and contact.customer_rank > 0 and account_d == 'True':
                        try:
                            sf.Account.delete(contact.salesforce_id)
                        except:
                            continue
                    else:
                        continue

            return super(CustomPartner, self).unlink()

        except Exception as e:
            raise Warning(_(str(e)))

    @api.model
    def create(self, values):
        try:
            res = super(CustomPartner, self).create(values)
            if 'salesforce_id' not in values:
                IrConfigParameter = self.env['ir.config_parameter'].sudo()
                username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
                password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
                security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
                enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
                contact_d = IrConfigParameter.get_param('odoo_salesforce.sf_contact')
                account_d = IrConfigParameter.get_param('odoo_salesforce.sf_account')
                if username and password and security and enabler == 'True' and (contact_d == 'True' or account_d == 'True'):
                    sf = Salesforce(username=username, password=password, security_token=security)

                    if res.salesforce_id:
                        if len(sf.quick_search(res.salesforce_id)) > 0:
                            if res.customer_rank == 0 and contact_d == 'True':
                                data = {
                                    'FirstName': res.first_name if res.first_name else None,
                                    'LastName': res.last_name if res.last_name else None,
                                    'Email': res.email if res.email else None,
                                    'OtherCity': res.city if res.city else None,
                                    'OtherStreet': res.street if res.street else None,
                                    'OtherCountry': self.env['res.country'].search([('id', '=', res.country_id.id)]).name if res.country_id else None,
                                    'OtherPostalCode': res.zip if res.zip else None,
                                    'Phone': res.phone if res.phone else None,
                                    'AccountId': res.parent_id.salesforce_id if res.parent_id.salesforce_id else None,
                                }
                                sf.Contact.update(res.salesforce_id, data)
                            elif res.customer_rank > 0 and account_d == 'True':
                                data = {
                                    'Name': res.name if res.name else None,
                                    'ShippingCity': res.city if res.city else None,
                                    'ShippingStreet': res.street if res.street else None,
                                    'ShippingCountry': self.env['res.country'].search([('id', '=', res.country_id.id)]).name if res.country_id else None,
                                    'ShippingPostalCode': res.zip if res.zip else None,
                                    'Phone': res.phone if res.phone else None,
                                }
                                sf.Account.update(res.salesforce_id, data)
                    else:
                        if res.customer_rank == 0 and contact_d == 'True':
                            data = {
                                    'FirstName': res.first_name if res.first_name else None,
                                    'LastName': res.last_name if res.last_name else None,
                                    'Email': res.email if res.email else None,
                                    'OtherCity': res.city if res.city else None,
                                    'OtherStreet': res.street if res.street else None,
                                    'OtherCountry': self.env['res.country'].search([('id', '=', res.country_id.id)]).name if res.country_id else None,
                                    'OtherPostalCode': res.zip if res.zip else None,
                                    'Phone': res.phone if res.phone else None,
                                    'AccountId': res.parent_id.salesforce_id if res.parent_id.salesforce_id else None,
                                }
                            new_contact = sf.Contact.create(data)
                        elif res.customer_rank > 0 and account_d == 'True':
                            data = {
                                    'Name': res.name if res.name else None,
                                    'ShippingCity': res.city if res.city else None,
                                    'ShippingStreet': res.street if res.street else None,
                                    'ShippingCountry': self.env['res.country'].search([('id', '=', res.country_id.id)]).name if res.country_id else None,
                                    'ShippingPostalCode': res.zip if res.zip else None,
                                    'Phone': res.phone if res.phone else None,
                                }
                            new_contact = sf.Account.create(data)
                        res.write({
                            'salesforce_id': new_contact['id']
                        })
                        self.env.cr.commit()
            return res
        except Exception as e:
            raise Warning(_(str(e)))

    def write(self, values):
        try:
            res = super(CustomPartner, self).write(values)
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
            contact_d = IrConfigParameter.get_param('odoo_salesforce.sf_contact')
            account_d = IrConfigParameter.get_param('odoo_salesforce.sf_account')
            if username and password and security and enabler == 'True' and (contact_d == 'True' or account_d == 'True'):
                sf = Salesforce(username=username, password=password, security_token=security)

                if self.salesforce_id:
                    if len(sf.quick_search(self.salesforce_id)) > 0:
                        if self.user_ids:
                            data = {
                                'Email': self.email if self.email else None,
                                'City': self.city if self.city else None,
                                'Street': self.street if self.street else None,
                                'Country': self.env['res.country'].search(
                                    [('id', '=', self.country_id.id)]).name if self.country_id else None,
                                'PostalCode': self.zip if self.zip else None,
                                'Phone': self.phone if self.phone else None,
                            }
                            sf.User.update(self.salesforce_id, data)
                        elif self.customer_rank == 0 and contact_d == 'True':
                            data = {
                                'FirstName': self.first_name if self.first_name else None,
                                'LastName': self.last_name if self.last_name else None,
                                'Email': self.email if self.email else None,
                                'OtherCity': self.city if self.city else None,
                                'OtherStreet': self.street if self.street else None,
                                'OtherCountry': self.env['res.country'].search(
                                    [('id', '=', self.country_id.id)]).name if self.country_id else None,
                                'OtherPostalCode': self.zip if self.zip else None,
                                'Phone': self.phone if self.phone else None,
                                'AccountId': self.parent_id.salesforce_id if self.parent_id.salesforce_id else None,
                            }
                            sf.Contact.update(self.salesforce_id, data)
                        elif self.customer_rank > 0 and account_d == 'True':
                            data = {
                                    'Name': self.name if self.name else None,
                                    'ShippingCity': self.city if self.city else None,
                                    'ShippingStreet': self.street if self.street else None,
                                    'ShippingCountry': self.env['res.country'].search([('id', '=', self.country_id.id)]).name if self.country_id else None,
                                    'ShippingPostalCode': self.zip if self.zip else None,
                                    'Phone': self.phone if self.phone else None,
                                }
                            sf.Account.update(self.salesforce_id, data)

            return res
        except Exception as e:
            raise Warning(_(str(e)))


class CustomLead(models.Model):
    _inherit = "crm.lead"

    salesforce_id = fields.Char(string="SalesForce Id")
    export_opportunities = fields.Boolean(_('Export To Salesforce'))
    active = fields.Boolean(string=_("Active"), track_visibility="onchange", default=True)
    sf_type = fields.Selection([("Existing Customer - Upgrade", "Existing Customer - Upgrade"),
                                ("Existing Customer - Replacement", "Existing Customer - Replacement"),
                                ("Existing Customer - Downgrade", "Existing Customer - Downgrade"),
                                ("New Customer", "New Customer")], string='Type')
    sf_industry = fields.Char(string="Industry")
    sf_title = fields.Char(string="Title")
    sf_status = fields.Selection([("Open - Not Contacted", "Open - Not Contacted"),
                                  ("Working - Contacted", "Working - Contacted"),
                                  ("Closed - Converted", "Closed - Converted"),
                                  ("Closed - Not Converted", "Closed - Not Converted")], string='Status')
    last_modified = fields.Char(string='Last Modified Date')
    location = fields.Char(string='Location')

    def unlink(self):
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
            lead_d = IrConfigParameter.get_param('odoo_salesforce.sf_lead')
            opportunity_d = IrConfigParameter.get_param('odoo_salesforce.sf_opportunity')

            if username and password and security and enabler == 'True' and (lead_d == 'True' or opportunity_d == 'True'):
                sf = Salesforce(username=username, password=password, security_token=security)
                for lead in self:
                    if lead.salesforce_id:
                        if lead.type == 'opportunity' and opportunity_d == 'True':
                            if len(sf.quick_search(lead.salesforce_id)) > 0:
                                sf.Opportunity.delete(lead.salesforce_id)
                        elif lead.type == 'lead' and lead_d == 'True':
                            if len(sf.quick_search(lead.salesforce_id)) > 0:
                                sf.Lead.delete(lead.salesforce_id)
                        else:
                            continue

            return super(CustomLead, self).unlink()

        except Exception as e:
            raise Warning(_(str(e)))

    @api.model
    def create(self, values):
        try:
            res = super(CustomLead, self).create(values)
            if 'salesforce_id' not in values:
                priority = None
                IrConfigParameter = self.env['ir.config_parameter'].sudo()
                username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
                password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
                security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
                enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
                lead_d = IrConfigParameter.get_param('odoo_salesforce.sf_lead')
                opportunity_d = IrConfigParameter.get_param('odoo_salesforce.sf_opportunity')

                if username and password and security and enabler == 'True' and (lead_d == 'True' or opportunity_d == 'True'):
                    sf = Salesforce(username=username, password=password, security_token=security)

                    if res.salesforce_id:
                        if res.type == 'opportunity' and opportunity_d == 'True':
                            if len(sf.quick_search(res.salesforce_id)) > 0:
                                date = str(datetime.now())
                                date_new, time = date.split(" ")
                                data = {
                                    'Name': res.name,
                                    'AccountId': res.partner_id.salesforce_id if res.partner_id.salesforce_id else None,
                                    'Amount': res.planned_revenue if res.planned_revenue else None,
                                    'CloseDate': res.date_closed if res.date_closed else date_new,
                                    'Description': res.description if res.description else None,
                                    'Probability': res.probability if res.probability else None,
                                    'StageName': res.stage_id.name if res.stage_id else None,
                                    'Type': res.sf_type if res.sf_type else None,
                                    'CampaignId': res.campaign_id.salesforce_id if res.campaign_id.salesforce_id else None,
                                    'LeadSource': res.source_id.name if res.source_id else None,
                                }
                                self.sales_force.Opportunity.update(res.salesforce_id, data)
                        else:
                            if len(sf.quick_search(res.salesforce_id)) > 0:
                                if res.priority == '3':
                                    priority = 'Hot'
                                elif res.priority == '2':
                                    priority = 'Warm'
                                elif res.priority == '1':
                                    priority = 'Cold'
                                else:
                                    priority = None
                                data = {
                                    'Salutation': res.title.name if res.title else None,
                                    'LastName': res.contact_name if res.contact_name else res.name,
                                    'Phone': res.partner_id.phone if res.partner_id.phone else None,
                                    'Company': res.name if res.name else None,
                                    'Email': res.email_from if res.email_from else None,
                                    'Industry': res.sf_industry if res.sf_industry else None,
                                    'Status': res.sf_status if res.sf_status else None,
                                    'AnnualRevenue': res.planned_revenue if res.planned_revenue else None,
                                    'Description': res.description if res.description else None,
                                    'LeadSource': res.source_id.name if res.source_id else None,
                                    'Rating': priority,
                                    'City': res.city if res.city else None,
                                    'Country': res.country_id.name if res.country_id else None,
                                    'PostalCode': res.zip if res.zip else None,
                                    'State': res.state_id.name if res.state_id else None,
                                    'Street': res.street if res.street else None,
                                    'Title': res.sf_title if res.sf_title else None,
                                }
                                self.sales_force.Lead.update(res.salesforce_id, data)
                    else:
                        if res.type == 'opportunity' and opportunity_d == 'True':
                            date = str(datetime.now())
                            date_new, time = date.split(" ")
                            data = {
                                'Name': res.name,
                                'AccountId': res.partner_id.parent_id.salesforce_id if res.partner_id.parent_id.salesforce_id else None,
                                'Amount': res.planned_revenue if res.planned_revenue else None,
                                'CloseDate': res.date_closed if res.date_closed else date_new,
                                'Description': res.description if res.description else None,
                                'Probability': res.probability if res.probability else None,
                                'StageName': res.stage_id.name if res.stage_id else None,
                                'Type': res.sf_type if res.sf_type else None,
                                'CampaignId': res.campaign_id.salesforce_id if res.campaign_id else None,
                                'LeadSource': res.source_id.name if res.source_id else None,
                            }
                            new_opportunity = sf.Opportunity.create(data)
                        else:
                            if res.priority == '3':
                                priority = 'Hot'
                            elif res.priority == '2':
                                priority = 'Warm'
                            elif res.priority == '1':
                                priority = 'Cold'
                            else:
                                priority = None
                            data = {
                                'Salutation': res.title.name if res.title else None,
                                'LastName': res.contact_name if res.contact_name else res.name,
                                'Phone': res.partner_id.phone if res.partner_id.phone else None,
                                'Company': res.name if res.name else None,
                                'Email': res.email_from if res.email_from else None,
                                'Industry': res.sf_industry if res.sf_industry else None,
                                'Status': res.sf_status if res.sf_status else None,
                                'AnnualRevenue': res.planned_revenue if res.planned_revenue else None,
                                'Description': res.description if res.description else None,
                                'LeadSource': res.source_id.name if res.source_id else None,
                                'Rating': priority,
                                'City': res.city if res.city else None,
                                'Country': res.country_id.name if res.country_id else None,
                                'PostalCode': res.zip if res.zip else None,
                                'State': res.state_id.name if res.state_id else None,
                                'Street': res.street if res.street else None,
                                'Title': res.sf_title if res.sf_title else None,
                            }
                            new_opportunity = sf.Lead.create(data)
                        res.write({
                            'salesforce_id': new_opportunity['id']
                        })
                        self.env.cr.commit()
            return res
        except Exception as e:
            raise Warning(_(str(e)))

    def write(self, values):
        try:
            res = super(CustomLead, self).write(values)
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
            lead_d = IrConfigParameter.get_param('odoo_salesforce.sf_lead')
            opportunity_d = IrConfigParameter.get_param('odoo_salesforce.sf_opportunity')

            if username and password and security and enabler == 'True' and (lead_d == 'True' or opportunity_d == 'True'):
                sf = Salesforce(username=username, password=password, security_token=security)

                if self.salesforce_id:
                    if self.type == 'opportunity' and opportunity_d == 'True':
                        if len(sf.quick_search(self.salesforce_id)) > 0:
                            if self.date_closed:
                                date = str(self.date_closed)
                                date_new, time = date.split(" ")
                            else:
                                date = str(datetime.now())
                                date_new, time = date.split(" ")
                            data = {
                                'Name': self.name,
                                'AccountId': self.partner_id.salesforce_id if self.partner_id.salesforce_id else None,
                                'Amount': self.planned_revenue if self.planned_revenue else None,
                                'CloseDate': date_new,
                                'Description': self.description if self.description else None,
                                'Probability': self.probability if self.probability else None,
                                'StageName': self.stage_id.name if self.stage_id else None,
                                'Type': self.sf_type if self.sf_type else None,
                                'CampaignId': self.campaign_id.salesforce_id if self.campaign_id.salesforce_id else None,
                                'LeadSource': self.source_id.name if self.source_id else None,
                            }
                            sf.Opportunity.update(self.salesforce_id, data)
                    else:
                        if len(sf.quick_search(self.salesforce_id)) > 0:
                            if self.priority == '3':
                                priority = 'Hot'
                            elif self.priority == '2':
                                priority = 'Warm'
                            elif self.priority == '1':
                                priority = 'Cold'
                            else:
                                priority = None
                            data = {
                                'Salutation': self.title.name if self.title else None,
                                'LastName': self.contact_name if self.contact_name else self.name,
                                'Phone': self.partner_id.phone if self.partner_id.phone else None,
                                'Company': self.name if self.name else None,
                                'Email': self.email_from if self.email_from else None,
                                'Industry': self.sf_industry if self.sf_industry else None,
                                'Status': self.sf_status if self.sf_status else None,
                                'AnnualRevenue': self.planned_revenue if self.planned_revenue else None,
                                'Description': self.description if self.description else None,
                                'LeadSource': self.source_id.name if self.source_id else None,
                                'Rating': priority,
                                'City': self.city if self.city else None,
                                'Country': self.country_id.name if self.country_id else None,
                                'PostalCode': self.zip if self.zip else None,
                                'State': self.state_id.name if self.state_id else None,
                                'Street': self.street if self.street else None,
                                'Title': self.sf_title if self.sf_title else None,
                            }
                            sf.Lead.update(self.salesforce_id, data)
            return res

        except Exception as e:
            raise Warning(_(str(e)))


class CustomContract(models.Model):
    _name = "sale.contract"

    salesforce_id = fields.Char(string="SalesForce Id")
    name = fields.Char(string="Contract Number")
    customer_id = fields.Many2one('res.partner', 'Account Name', required=True)
    sf_status = fields.Selection([("Draft", "Draft"), ("In Approval Process", "In Approval Process"),
                                  ("Activated", "Activated")], string='Status', required=True)
    start_date = fields.Datetime(string='Contract Start Date', required=True)
    end_date = fields.Datetime(string='Contract End Date', compute="_end_date")
    term_months = fields.Integer(string="Contract Term(months)", required=True)
    last_modified = fields.Char(string='Last Modified Date')
    location = fields.Char(string='Location')

    def _end_date(self):
        for record in self:
            record.end_date = record.start_date + relativedelta(months=+record.term_months)

    def unlink(self):
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
            contract_d = IrConfigParameter.get_param('odoo_salesforce.sf_contract')

            if username and password and security and enabler == 'True' and contract_d == 'True':
                sf = Salesforce(username=username, password=password, security_token=security)
                for contract in self:
                    if contract.salesforce_id:
                        if len(sf.quick_search(contract.salesforce_id)) > 0:
                            sf.Contract.delete(contract.salesforce_id)
            return super(CustomContract, self).unlink()

        except Exception as e:
            raise Warning(_(str(e)))

    @api.model
    def create(self, values):
        try:
            res = super(CustomContract, self).create(values)
            if 'salesforce_id' not in values:
                priority = None
                IrConfigParameter = self.env['ir.config_parameter'].sudo()
                username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
                password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
                security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
                enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
                contract = IrConfigParameter.get_param('odoo_salesforce.sf_contract')

                if username and password and security and enabler == 'True' and contract == 'True':
                    sf = Salesforce(username=username, password=password, security_token=security)

                    if res.salesforce_id:
                        if len(sf.quick_search(res.salesforce_id)) > 0:
                            data = {
                                'AccountId': res.name.salesforce_id if res.name.salesforce_id else None,
                                'Status': res.sf_status if res.sf_status else None,
                                'ContractTerm': res.term_months if res.term_months else None,
                                'OwnerId': self.env.user.salesforce_id if self.env.user.salesforce_id else None,
                                'StartDate': str(res.start_date).split(" ")[0] if res.start_date else None,
                            }
                            self.sales_force.Contract.update(res.salesforce_id, data)
                    else:
                        data = {
                            'AccountId': res.name.salesforce_id if res.name.salesforce_id else None,
                            'Status': res.sf_status if res.sf_status else None,
                            'ContractTerm': res.term_months if res.term_months else None,
                            'OwnerId': self.env.user.salesforce_id if self.env.user.salesforce_id else None,
                            'StartDate': str(res.start_date).split(" ")[0] if res.start_date else None,
                        }
                        new_contract = sf.Contract.create(data)
                        # query = "select ContractNumber from contract where id="
                        # extended_query = str(new_contract['id'])
                        # contract = sf.query(query+extended_query)["records"]
                        res.write({
                            'salesforce_id': new_contract['id'],
                            # 'contract_number': contract['ContractNumber']
                        })
                        self.env.cr.commit()
            return res
        except Exception as e:
            raise Warning(_(str(e)))

    def write(self, values):
        try:
            res = super(CustomContract, self).write(values)
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
            lead_d = IrConfigParameter.get_param('odoo_salesforce.sf_lead')

            if username and password and security and enabler == 'True' and lead_d == 'True':
                sf = Salesforce(username=username, password=password, security_token=security)

                if self.salesforce_id:
                    if len(sf.quick_search(self.salesforce_id)) > 0:
                        data = {
                            'AccountId': self.name.salesforce_id if self.name.salesforce_id else None,
                            'Status': self.sf_status if self.sf_status else None,
                            'ContractTerm': self.term_months if self.term_months else None,
                            'OwnerId': self.env.user.salesforce_id if self.env.user.salesforce_id else None,
                            'StartDate': str(self.start_date).split(" ")[0] if self.start_date else None,
                        }
                        self.sales_force.Contract.update(self.salesforce_id, data)
            return res

        except Exception as e:
            raise Warning(_(str(e)))


class CustomOrder(models.Model):
    _inherit = "sale.order"

    salesforce_id_so = fields.Char(string="SalesForce Id SO")
    salesforce_id_qo = fields.Char(string="SalesForce Id Quotation")
    export_order = fields.Boolean('Export To Salesforce')
    sf_name = fields.Char(string="Quote Name")
    sf_status_so = fields.Selection([("Draft", "Draft"), ("Activated", "Activated")], string='Salesforce Status')
    sf_status_qo = fields.Selection([("Draft", "Draft"), ("Needs Review", "Needs Review"),
                                     ("In Review", "In Review"), ("Approved", "Approved"),
                                     ("Rejected", "Rejected"), ("Presented", "Presented"),
                                     ("Accepted", "Accepted"), ("Denied", "Denied")], string='Salesforce Status')
    contract_id = fields.Many2one('sale.contract', 'Contract Number')
    last_modified = fields.Char(string='Last Modified Date')
    location = fields.Char(string='Location')

    def unlink(self):
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
            order = IrConfigParameter.get_param('odoo_salesforce.sf_saleorder')

            if username and password and security and enabler == 'True' and order == 'True':
                sf = Salesforce(username=username, password=password, security_token=security)
                for order in self:
                    if order.state == 'draft':
                        if order.salesforce_id:
                            if len(sf.quick_search(order.salesforce_id)) > 0:
                                sf.Quote.delete(order.salesforce_id_qo)
                    elif order.state == 'sale':
                        if order.salesforce_id:
                            if len(sf.quick_search(order.salesforce_id)) > 0:
                                sf.Order.delete(order.salesforce_id_so)
                    else:
                        continue

            return super(CustomOrder, self).unlink()

        except Exception as e:
            raise Warning(_(str(e)))


class CustomProduct(models.Model):
    _inherit = "product.template"

    salesforce_id = fields.Char(string="SalesForce Id")
    sf_product_family = fields.Many2one('product.family', string="Product Family")
    last_modified = fields.Char(string='Last Modified Date')
    location = fields.Char(string='Source')

    @api.model
    def create(self, values):
        try:
            res = super(CustomProduct, self).create(values)
            if 'salesforce_id' not in values:
                IrConfigParameter = self.env['ir.config_parameter'].sudo()
                username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
                password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
                security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
                enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
                product_d = IrConfigParameter.get_param('odoo_salesforce.sf_product')

                if username and password and security and enabler == 'True' and product_d == 'True':
                    sf = Salesforce(username=username, password=password, security_token=security)

                    if res.salesforce_id:
                        if len(sf.quick_search(res.salesforce_id)) > 0:
                            data = {
                                'Name': res.name,
                                'Description': res.description if res.description else None,
                                'ProductCode': res.default_code if res.default_code else None,
                            }
                            sf.Product2.update(res.salesforce_id, data)
                    else:
                        data = {
                            'Name': res.name,
                            'Description': res.description if res.description else None,
                            'ProductCode': res.default_code if res.default_code else None,
                        }
                        new_contact = sf.Product2.create(data)
                        res.write({
                            'salesforce_id': new_contact['id']
                        })
                        self.env.cr.commit()
            return res
        except Exception as e:
            raise Warning(_(str(e)))

    def write(self, values):
        try:
            res = super(CustomProduct, self).write(values)
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
            product_d = IrConfigParameter.get_param('odoo_salesforce.sf_product')

            if username and password and security and enabler == 'True' and product_d == 'True':
                sf = Salesforce(username=username, password=password, security_token=security)

                if self.salesforce_id:
                    if len(sf.quick_search(self.salesforce_id)) > 0:
                        data = {
                            'Name': self.name,
                            'Description': self.description if self.description else None,
                            'ProductCode': self.default_code if self.default_code else None,
                        }
                        sf.Product2.update(self.salesforce_id, data)
            return res

        except Exception as e:
            raise Warning(_(str(e)))

    def unlink(self):
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
            product_d = IrConfigParameter.get_param('odoo_salesforce.sf_product')

            if username and password and security and enabler == 'True' and product_d == 'True':
                sf = Salesforce(username=username, password=password, security_token=security)
                for product in self:
                    if product.salesforce_id:
                        if len(sf.quick_search(product.salesforce_id)) > 0:
                            sf.Product2.delete(product.salesforce_id)
            return super(CustomProduct, self).unlink()
        except Exception as e:
            raise Warning(_(str(e)))


class CustomProductFamily(models.Model):
    _name = "product.family"

    name = fields.Char(string="Product Family")


class CustomActivity(models.Model):
    _inherit = 'mail.activity'

    salesforce_id = fields.Char('Salesforce Id')
    sf_status = fields.Selection([("Not Started", "Not Started"), ("In Progress", "In Progress"),
                                  ("Completed", "Completed"), ("Waiting on someone else", "Waiting on someone else"),
                                  ("Deferred", "Deferred")], string='Status')
    sf_priority = fields.Selection([("High", "High"), ("Normal", "Normal"), ("Low", "Low")], string='Status')
    last_modified = fields.Char(string='Last Modified Date')

    @api.model
    def create(self, values):
        try:
            res = super(CustomActivity, self).create(values)
            if 'salesforce_id' not in values:
                IrConfigParameter = self.env['ir.config_parameter'].sudo()
                username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
                password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
                security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
                enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
                task_d = IrConfigParameter.get_param('odoo_salesforce.sf_task')

                if username and password and security and enabler == 'True' and task_d == 'True':
                    sf = Salesforce(username=username, password=password, security_token=security)

                    if res.salesforce_id:
                        if len(sf.quick_search(res.salesforce_id)) > 0:
                            whoid = self.env['res.partner'].search([('id', '=', res.res_id)]).salesforce_id
                            data = {
                                'Subject': res.activity_type_id.name,
                                'Status': res.sf_status if res.sf_status else None,
                                'Priority': res.sf_priority if res.sf_priority else None,
                                'Description': res.summary if res.summary else None,
                                'WhoId': whoid if whoid else None,
                                'ActivityDate': str(res.date_deadline) if res.date_deadline else None,
                                'OwnerId': res.user_id.salesforce_id if res.user_id.salesforce_id else None,
                            }
                            sf.Task.update(res.salesforce_id, data)
                    else:
                        whoid = self.env['res.partner'].search([('id', '=', res.res_id)]).salesforce_id
                        data = {
                            'Subject': res.activity_type_id.name,
                            'Status': res.sf_status if res.sf_status else None,
                            'Priority': res.sf_priority if res.sf_priority else None,
                            'Description': res.summary if res.summary else None,
                            'WhoId': whoid if whoid else None,
                            'ActivityDate': str(res.date_deadline) if res.date_deadline else None,
                            'OwnerId': res.user_id.salesforce_id if res.user_id.salesforce_id else None,
                        }
                        new_contact = sf.Task.create(data)
                        res.write({
                            'salesforce_id': new_contact['id']
                        })
                        self.env.cr.commit()
            return res
        except Exception as e:
            raise Warning(_(str(e)))

    def write(self, values):
        try:
            res = super(CustomActivity, self).write(values)
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
            task_d = IrConfigParameter.get_param('odoo_salesforce.sf_task')

            if username and password and security and enabler == 'True' and task_d == 'True':
                sf = Salesforce(username=username, password=password, security_token=security)
                if self.salesforce_id:
                    if len(sf.quick_search(self.salesforce_id)) > 0:
                        whoid = self.env['res.partner'].search([('id', '=', self.res_id)]).salesforce_id
                        data = {
                            'Subject': self.activity_type_id.name,
                            'Status': self.sf_status if self.sf_status else None,
                            'Priority': self.sf_priority if self.sf_priority else None,
                            'Description': self.summary if self.summary else None,
                            'WhoId': whoid if whoid else None,
                            'ActivityDate': str(self.date_deadline) if self.date_deadline else None,
                            'OwnerId': self.user_id.salesforce_id if self.user_id.salesforce_id else None,
                        }
                        sf.Task.update(self.salesforce_id, data)
            return res

        except Exception as e:
            raise Warning(_(str(e)))

    def unlink(self):
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
            task_d = IrConfigParameter.get_param('odoo_salesforce.sf_task')

            if username and password and security and enabler == 'True' and task_d == 'True':
                sf = Salesforce(username=username, password=password, security_token=security)
                for task in self:
                    if task.salesforce_id:
                        if len(sf.quick_search(task.salesforce_id)) > 0:
                            sf.Task.delete(task.salesforce_id)

            return super(CustomActivity, self).unlink()
        except Exception as e:
            raise Warning(_(str(e)))


class SalesforceOpportunityCampaign(models.Model):
    _inherit = 'utm.campaign'

    salesforce_id = fields.Char(string="SalesForce Id")


class CustomCalendar(models.Model):
    _inherit = 'calendar.event'

    salesforce_id = fields.Char(string="SalesForce Id")
    last_modified = fields.Char(string='Last Modified Date')
    sf_location = fields.Char(string='SaleForce/Odoo')

    @api.model
    def create(self, values):
        try:
            res = super(CustomCalendar, self).create(values)
            if 'salesforce_id' not in values:
                IrConfigParameter = self.env['ir.config_parameter'].sudo()
                username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
                password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
                security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
                enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
                event_d = IrConfigParameter.get_param('odoo_salesforce.sf_event')

                if username and password and security and enabler == 'True' and event_d == 'True':
                    sf = Salesforce(username=username, password=password, security_token=security)

                    if res.salesforce_id:
                        if len(sf.quick_search(res.salesforce_id)) > 0:
                            data = {
                                'Subject': res.display_name,
                                'StartDateTime': res.start.strftime('%Y-%m-%dT%H:%M:%S') if res.start else None,
                                'EndDateTime': res.stop.strftime('%Y-%m-%dT%H:%M:%S') if res.stop else None,
                                'Description': res.description if res.description else None,
                                'IsAllDayEvent': res.allday,
                                'Location': res.location if res.location else None,
                                'OwnerId': self.env.user.salesforce_id,
                            }
                            sf.Event.update(res.salesforce_id, data)
                    else:
                        data = {
                            'Subject': res.display_name,
                            'StartDateTime': res.start.strftime('%Y-%m-%dT%H:%M:%S') if res.start else None,
                            'EndDateTime': res.stop.strftime('%Y-%m-%dT%H:%M:%S') if res.stop else None,
                            'Description': res.description if res.description else None,
                            'IsAllDayEvent': res.allday,
                            'Location': res.location if res.location else None,
                            'OwnerId': self.env.user.salesforce_id,
                        }
                        new_contact = sf.Event.create(data)
                        res.write({
                            'salesforce_id': new_contact['id']
                        })
                        self.env.cr.commit()
            return res
        except Exception as e:
            raise Warning(_(str(e)))

    def write(self, values):
        try:
            res = super(CustomCalendar, self).write(values)
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
            event_d = IrConfigParameter.get_param('odoo_salesforce.sf_event')

            if username and password and security and enabler == 'True' and event_d == 'True':
                sf = Salesforce(username=username, password=password, security_token=security)

                if self.salesforce_id:
                    if len(sf.quick_search(self.salesforce_id)) > 0:
                        data = {
                            'Subject': self.display_name,
                            'StartDateTime': self.start.strftime('%Y-%m-%dT%H:%M:%S') if self.start else None,
                            'EndDateTime': self.stop.strftime('%Y-%m-%dT%H:%M:%S') if self.stop else None,
                            'Description': self.description if self.description else None,
                            'IsAllDayEvent': self.allday,
                            'Location': self.location if self.location else None,
                            'OwnerId': self.env.user.salesforce_id,
                        }
                        sf.Event.update(self.salesforce_id, data)
            return res

        except Exception as e:
            raise Warning(_(str(e)))

    def unlink(self):
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            enabler = IrConfigParameter.get_param('odoo_salesforce.sf_salesforce_enable')
            event_d = IrConfigParameter.get_param('odoo_salesforce.sf_event')

            if username and password and security and enabler == 'True' and event_d == 'True':
                sf = Salesforce(username=username, password=password, security_token=security)
                for event in self:
                    if event.salesforce_id:
                        if len(sf.quick_search(event.salesforce_id)) > 0:
                            sf.Event.delete(event.salesforce_id)

            return super(CustomCalendar, self).unlink()
        except Exception as e:
            raise Warning(_(str(e)))
