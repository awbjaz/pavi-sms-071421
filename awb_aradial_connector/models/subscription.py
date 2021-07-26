from ..helpers.password_generator import GeneratePassword
from odoo import api, fields, models, exceptions, _
from openerp.exceptions import Warning

import logging

_logger = logging.getLogger(__name__)

class Subscription(models.Model):
    _inherit = 'sale.subscription'

    state = fields.Char("State", compute='_get_stage_name')
    product_names = fields.Char("Products", compute='_get_subs_product_names')
    product_desc = fields.Char("Products Description", compute='_get_subs_product_names')

    @api.model
    def create(self, vals):
        vals['stage_id'] = self.env['sale.subscription.stage'].search([("name", "=", "Draft")]).id
        vals['in_progress'] = False

        res = super(Subscription, self).create(vals)
        return res

    @api.depends('stage_id')
    def _get_stage_name(self):
        for rec in self:
            rec.state = rec.stage_id.name

    @api.depends('recurring_invoice_line_ids')
    def _get_subs_product_names(self):
        products = []
        desc = []
        for rec in self:
            for line_item in rec.recurring_invoice_line_ids:
                if line_item.product_id.type == 'service':
                    products.append(line_item.display_name)
                    desc.append(line_item.name)  # description
                    desc.append(str(line_item.quantity))
                    if line_item.date_start:
                        desc.append(line_item.date_start.strftime("%b %d, %Y"))
            rec.product_names = ', '.join(products)
            rec.product_desc = ', '.join(desc)

    def create_aradial_user(
        self,
        record=None
    ):
        
        _logger.info("=== Subscription ===")

        if not record:
            raise exceptions.ValidationError(
                ("Record is required")
            )
        self.record = record
        
        is_valid = self._validate_parameters(
            record.subscriber_location_id,
            record.atm_ref,
            record.stage_id.name
        )

        if is_valid == True:

            products = ""

            for line_id in record.recurring_invoice_line_ids:
                products += line_id.product_id.display_name.upper()
            first_name = record.partner_id.first_name
            last_name = record.partner_id.last_name
            if not first_name:
                first_name = record.partner_id.name
                last_name = ''

            pw = GeneratePassword()
            password = pw.generate_password()

            self.data = {
                'UserID': record.code,
                'Password': password,
                'FirstName': first_name,
                'LastName': last_name,
                'Address1': record.partner_id.street,
                'Address2': record.partner_id.street2,
                'City': record.partner_id.city,
                'State': record.partner_id.state_id.name,
                'Country': record.partner_id.country_id.name,
                'Zip': record.partner_id.zip,
                'Offer': products,
                'ServiceType': 'Internet',
                # 'Start Date': str(record.date_start,
                'CustomInfo1': 'VDH',
                'CustomInfo2': 'Postpaid',
                'CustomInfo3': record.partner_id.customer_number,
            }

            _logger.info("User Details:")
            _logger.info("UserID: %s" % self.data['UserID'])
            _logger.info("Offer: %s" % self.data['Offer'])
            _logger.info("First Name: %s" % self.data['FirstName'])
            _logger.info("Last Name: %s" % self.data['LastName'])

            isUserCreationSuccessful = self.env['aradial.connector'].create_user(self.data)

            if isUserCreationSuccessful:
                self.record.write({
                    'stage_id': self.env['sale.subscription.stage'].search([("name", "=", "In Progress")]).id,
                    'in_progress': True
                })
            else:
                raise Warning("User Creation in Aradial: FAILED")

    def _validate_parameters(
        self,
        location,
        atm_ref,
        stage
    ):
        _logger.info("Validating Subcription")

        if not location:
            _logger.info("Location is required")
            return False
        if not atm_ref:
            _logger.info("atm_ref is required")
            return False
        if stage != 'Draft':
            _logger.info("Stage should be in Draft")
            return False

        _logger.info("Valid Subscription")
        return True

    def _send_welcome_message(self, recordset, template_name, state):
        self.env['awb.sms.send'].send_now(
            recordset=recordset,
            template_name=template_name,
            state=state
        )
        _logger.info("----- SMS Sending Done -----")
