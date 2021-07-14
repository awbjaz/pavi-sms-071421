# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Batch Refund",
    'summary': """
        AWB Batch Refund
        """,
    'description': """
        AWB Batch Refund """,
    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",
    'category': 'Accounting/Accounting',
    'version': '13.0.1.3.3',
    'depends': ['account', 'awb_subscriber_location'],
    'data': [
        'data/account_move_rebate_sequence.xml',
        'security/ir.model.access.csv',
        'views/account_move_batch_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
