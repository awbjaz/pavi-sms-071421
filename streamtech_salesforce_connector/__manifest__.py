# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "Streamtech Salesforce Connector",
    'summary': """
        StreamTech Specific Salesforce Connector
        """,
    'description': """
        Includes the customization for Streamtech's Salesforce
    """,
    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",
    'category': 'Sales',
    'version': '13.0.1.0.3',
    'depends': ['salesforce_connector', 'awb_subscriber_bill_automation', 'awb_subscriber_product_information'],
    'data': [
        'views/crm_view.xml',
        'views/partner_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
