# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Subscriber Bill Automation",

    'summary': """
        Subscriber Bill Automation.
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '13.0.1.3.0',

    'depends': ['crm', 'sale_management', 'sale_subscription', 'awb_subscriber_product_information'],

    'data': [
        # 'security/ir.model.access.csv',
        'data/crm_data.xml',
        'data/subscription_atm_ref_sequence.xml',
        'views/crm_view.xml',
        'views/sale_view.xml',
        'views/subscription_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False

}
