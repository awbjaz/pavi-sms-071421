# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Bill Pre-Termination",

    'summary': """
        Bill Pre-Termination Module.
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders Inc.",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '13.0.1.0.0',

    'depends': ['sale_subscription', 'awb_subscriber_bill_automation'],

    'data': [
        'data/product_data.xml',
        'views/sale_subscription_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False

}
