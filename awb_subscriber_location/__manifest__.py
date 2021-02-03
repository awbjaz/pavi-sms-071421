# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Subscriber Location",

    'summary': """
        Subscriber's Location Module.
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '13.0.1.0.0',

    'depends': ['account_accountant', 'base_address_city', 'contacts', 'hr', 'mail', 'project', 'sale_management', 'sale_subscription'],

    'data': [
        'security/ir.model.access.csv',
        'views/brand_view.xml',
        'views/project_view.xml',
        'views/city_view.xml',
        'views/sale_subscription_view.xml',
        'views/sale_view.xml',
        'views/subscriber_location_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False

}
