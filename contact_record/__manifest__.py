# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Contact Record",

    'summary': """
        Contact Record.
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders Inc.",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '13.0.2.0.0',

    'depends': [
                'base_address_city',
                'contacts',
                'crm',
                'purchase',
                'sale_management'
    ],

    'data': [
        'data/res_regions.xml',
        'data/res_provinces.xml',
        'data/res_cities.xml',
        'security/ir.model.access.csv',
        'views/res_region_view.xml',
        'views/res_province_view.xml',
        'views/crm_lead_view.xml',
        'views/res_partner_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
