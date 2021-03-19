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

    'version': '13.0.1.1.0',

    'depends': ['approvals', 'product'],

    'data': [
        'security/ir.model.access.csv',
        'views/approval_view.xml',
    ],
}
