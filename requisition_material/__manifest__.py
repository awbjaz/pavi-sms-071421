# -*- coding: utf-8 -*-
{
    'name': "AWB Material Requisition",

    'summary': """
        Material Requisition""",

    'description': """
        Material Requisition
    """,

    'author': "Achieve Without Borders Inc.",
    'website': "https://www.achievewithoutborders.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '13.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': [
                'approvals',
                'requisition_approval',
                'stock'
    ],

    # always loaded
    'data': [
        'views/approval_category_views.xml',
        'views/approval_request_views.xml',
        'views/mail_templates.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
