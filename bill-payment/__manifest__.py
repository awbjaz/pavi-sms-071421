# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "Streamtech Subscriber Bill Payment",

    'summary': """
        Subscriber Bill Payment
        """,

    'description': """
        Subscriber Bill Payment
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '13.0.1.1.0',

    'depends': ['awb_subscriber_bill', 'awb_subscriber_bill_automation'],

    'data': [
        'views/account_payment_views.xml'
    ],
    'qweb': [
        # 'static/src/xml/account_invoice_tree_header.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False

}
