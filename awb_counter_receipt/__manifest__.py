# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Counter Receipt",

    'summary': """
        Counter Receipt Module.
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '13.0.1.0.0',

    'depends': ['base', 'purchase', 'stock', 'account'],

    'data': [
        # 'security/ir.model.access.csv',
        'data/purchase_data.xml',
        'reports/counter_receipt.xml',
        'reports/report_format.xml',
        'views/picking_view.xml',
        'views/purchase_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False

}
