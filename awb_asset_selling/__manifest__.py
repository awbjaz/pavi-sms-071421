# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Asset Selling",
    'summary': """
        AWB Asset Selling
        """,
    'description': """
        AWB Asset Selling """,
    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",
    'category': 'Accounting/Asset',
    'version': '13.0.1.0.0',
    'depends': ['account', 'account_asset'],
    'data': [
        'wizards/account_asset_sell_wiz.xml',
        'views/account_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
