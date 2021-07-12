# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Amount Based Approvals",

    'summary': """
        Amount Based Approvals
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Approvals',

    'version': '13.0.1.0.0',

    'depends': ['approvals'],

    'data': [
        'security/ir.model.access.csv',
        'views/approval_rules_view.xml',
    ],
}
