# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Payment Internal Transfer",
    'summary': """
        AWB Payment Internal Transfer
        """,
    'description': """
        AWB Payment Internal Transfer """,
    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",
    'category': 'Accounting/Payments',
    'version': '13.0.1.2.1',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_payment_view.xml',
        'wizards/create_internal_transfer_wizard.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
