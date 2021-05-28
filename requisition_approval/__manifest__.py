# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "Requisition Approvals",

    'summary': """
        Requisition Approvals
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Approval',

    'version': '13.0.1.4.0',

    'depends': ['approvals', 'product'],

    'data': [
        'security/ir.model.access.csv',
        'security/ir.rule.csv',
        'views/approval_view.xml',
    ],
}
