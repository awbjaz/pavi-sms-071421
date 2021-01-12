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

    'depends': ['account_accountant', 'sale_subscription'],

    'data': [
        'security/ir.model.access.csv',
        'data/cost_allocation_sequence.xml',
        'views/account_move_line_view_ext.xml',
        'views/cost_allocation_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False

}
