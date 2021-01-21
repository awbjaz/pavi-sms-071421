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

    'version': '13.0.1.0.0',

    'depends': ['crm', 'sale_management', 'sale_subscription'],

    'data': [
        # 'security/ir.model.access.csv',
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
