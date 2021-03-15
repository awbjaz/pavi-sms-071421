# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Report Header",

    'summary': """
        Report Header Module.
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '13.0.1.0.0',

    'depends': ['base', 'web'],

    'data': [
        # 'security/ir.model.access.csv',
        'reports/report_templates.xml',
    ],
     # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False

}
