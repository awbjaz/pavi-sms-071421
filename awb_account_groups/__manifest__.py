# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Account Groups",

    'summary': """
        Account Groups Module.
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '13.0.1.0.0',

    'depends': ['hr_expense', 'account_accountant', 'account_asset'],

    'data': [
        # 'security/ir.model.access.csv',
        'security/ir.rule.csv',
        'views/account_view.xml',
        'views/hr_expense_view.xml',
    ],
     # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False

}
