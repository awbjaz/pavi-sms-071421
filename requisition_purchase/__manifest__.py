# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Purchase Requisition",

    'summary': """
        Purchase Requisition
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '13.0.1.4.2',

    'depends': ['requisition_approval', 'purchase_requisition', 'purchase', 'stock', 'purchase_stock'],

    'data': [
        'security/ir.model.access.csv',
        'views/approval_category_views.xml',
        'views/approval_request_views.xml',
        'views/purchase_order_views.xml',
        'views/purchase_requisition_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
