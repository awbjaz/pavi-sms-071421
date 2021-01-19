# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Asset Updates",

    'summary': """
        Asset Updates Module.
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '13.0.1.0.0',

    'depends': ['account_asset', 'account_accountant'],

    'data': [
        'data/account_asset_sequence.xml',
        'security/ir.model.access.csv',
        'views/account_asset_category_view.xml',
        'views/account_asset_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False

}