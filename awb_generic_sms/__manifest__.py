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

    'version': '13.0.1.1.1',

    'depends': [
        'base',
        'account_accountant',
        'sale_subscription',
        'awb_subscriber_bill'
    ],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/send_sms_view.xml',
        'views/menuitem.xml',
        'views/res_config_settings.xml',
        'views/sms_invoice_view.xml',
        'views/sms_payment_view.xml',
        'data/set_access_rights.xml',
        'data/account_move_data.xml',
        'data/account_payment_data.xml',
        'data/awb_sms_template_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False

}