# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Asset Depreciation",

    'summary': """
        Asset Depreciation.
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Accounting/Accounting',

    'version': '13.0.2.0.0',

    'depends': ['account_asset'],

    'data': [
        'security/ir.model.access.csv',
        'views/account_asset_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False

}
