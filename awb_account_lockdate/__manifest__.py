# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Account Lock Date",

    'summary': """
        Account Lock Date.
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders Inc.",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '13.0.1.0.0',

    'depends': ['account', 'account_accountant'],

    'data': [
        'wizard/account_change_lock_date.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False

}
