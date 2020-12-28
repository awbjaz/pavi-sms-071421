# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "Streamtech Official Receipt",
    'summary': """
        Official Receipt print out
        """,
    'description': """
        Streamtech Official Receipt Template
    """,
    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",
    'category': 'Report',
    'version': '13.0.1.0.0',
    'depends': ['account'],
    'data': [
        'reports/report.xml',
        'reports/official_receipt.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
