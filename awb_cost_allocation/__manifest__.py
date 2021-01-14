# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Cost Allocation",

    'summary': """
        Cost Allocation.
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders Inc.",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '13.0.1.0.0',

    'depends': ['account_accountant', 'sale_subscription', 'awb_subscriber_location'],

    'data': [
        'data/cost_allocation_sequence.xml',
        'security/ir.model.access.csv',
        'views/product_view_ext.xml',
        'views/cost_allocation_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False

}
