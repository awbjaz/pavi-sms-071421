from odoo import api, fields, models, exceptions, _
from openerp.exceptions import Warning

import logging

_logger = logging.getLogger(__name__)

class Subscription(models.Model):
    _inherit = 'sale.subscription'

    
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
                products += line_id.product_id.display_name
            first_name = record.partner_id.first_name
            last_name = record.partner_id.last_name

            self.data = {
                'UserID': record.code,
                'Password': 'password',         # TODO: call password generator
                'Offer': products,
	      	    'ServiceType': 'Internet',
	      	    'FirstName': first_name,
 	      	    'LastName': last_name,
	            'CustomInfo1': 'VDH'
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

# YAN: commenting out the checking for location - for testing
#         if not location:
#             _logger.info("Location is required")
#             return False
        if not atm_ref:
            _logger.info("atm_ref is required")
            return False
        if stage != 'Draft':
            _logger.info("Stage should be in Draft")
            return False

        _logger.info("Valid Subscription")
        return True



