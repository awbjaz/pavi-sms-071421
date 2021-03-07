# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Subscriber's Bill",

    'summary': """
        Subscriber's Bill.
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '13.0.1.0.0',

    'depends': ['account_accountant', 'sale_subscription'],

    'data': [
        'security/ir.model.access.csv',
        'data/account_move_atm_ref_sequence.xml',
        'data/account_data.xml',
        # 'views/assets.xml',
        'views/account_view.xml',
        'views/account_printer_data.xml',
        'views/company_view.xml',
        'report/statement_of_account_report.xml',
    ],
    'qweb': [
        # 'static/src/xml/account_invoice_tree_header.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False

}
