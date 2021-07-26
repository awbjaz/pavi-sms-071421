# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Aradial Connector",
    'summary': """
        Odoo - Aradial Connector
        """,
    'description': """
        Odoo - Aradial Connector
    """,
    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",
    'category': 'Sales',
    'version': '13.0.1.0.1',
    'depends': ['base', 'crm', 'sale_management', 'sale_subscription', 'awb_subscriber_product_information'],
    'data': [
        'data/sale_subscription_data.xml',
        'data/awb_sms_template_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
