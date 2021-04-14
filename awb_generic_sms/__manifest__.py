# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Generic SMS",

    'summary': """
        AWB Generic SMS
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Sms Integration',

    'version': '13.0.1.0.0',

    'depends': ['account_accountant'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/send_sms_view.xml',
        'views/menuitem.xml',
        'views/res_config_settings.xml',
        # 'views/sms_invoice_view.xml',
        'data/sms_template_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False

}