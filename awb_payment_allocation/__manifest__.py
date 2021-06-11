# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Payment Allocation",
    'summary': """
        AWB Payment Allocation
        """,
    'description': """
        AWB Payment Allocation """,
    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",
    'category': 'Accounting/Accounting',
    'version': '13.0.1.0.1',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_payment_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
