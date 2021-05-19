# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Purchase Order Approval",
    'summary': """
        AWB Purchase Order Approval
        """,
    'description': """
        AWB Purchase Order Approval
    """,
    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",
    'category': "Operations/Purchase",
    'version': '13.0.1.6.0',
    'depends': ['web', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'security/ir.rule.csv',
        'data/mail_data.xml',
        'views/purchase_order_approval_views.xml',
        'views/purchase_views.xml',
        'report/purchase_report_templates.xml',
        'report/purchase_quotation_templates.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
