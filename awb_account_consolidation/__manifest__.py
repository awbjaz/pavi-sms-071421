# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Account Consolidation",
    'summary': """
        AWB Account Consolidation
        """,
    'description': """
        AWB Account Consolidation
    """,
    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",
    'category': 'Report',
    'version': '13.0.1.0.0',
    'depends': ['account_consolidation'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
