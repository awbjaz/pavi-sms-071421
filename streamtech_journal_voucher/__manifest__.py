# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "Journal Voucher",
    'summary': """
        Journal Voucher print out
        """,
    'description': """
        Streamtech Journal Voucher Template
    """,
    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",
    'category': 'Report',
    'version': '13.0.1.0.0',
    'depends': ['account'],
    'data': [
        'views/account_move_views.xml',
        'reports/report.xml',
        'reports/journal_voucher.xml',
        'reports/account_payable_voucher.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
