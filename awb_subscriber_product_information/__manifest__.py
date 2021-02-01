# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Subscriber and Product Information",

    'summary': """
        AWB Subscriber and Product Information for Streamtech
        """,

    'description': """
        AWB Subscriber and Product Information for Streamtech
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '13.0.1.1.0',

    'depends': ['crm', 'sale_management', 'sale_subscription', 'awb_subscriber_location'],

    'data': [
        'data/crm_stage_data.xml',
        'security/ir.model.access.csv',
        'views/crm_view.xml',
        'views/partner_view.xml',
        'views/product_view_ext.xml',
        'views/sale_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'installable': True,
    'application': False,
    'auto_install': False

}
