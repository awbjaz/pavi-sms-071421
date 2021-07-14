# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Account Aging Reports",
    'summary': """
        AWB Account Aging Reports
        """,
    'description': """
        AWB Account Aging Reports
    """,
    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",
    'category': 'Report',
    'version': '13.0.1.0.0',
    'depends': ['account', 'account_reports'],
    'data': [
        'views/account_report_view.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
