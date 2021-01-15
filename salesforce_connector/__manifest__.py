# -*- coding: utf-8 -*-
{
    'name': "Odoo Salesforce Connector",
    'version': '13.0.0.0.1',
    'category': 'Sales',
    'summary': 'ODOO Salesforce',
    'author': 'Techloyce',
    'website': 'http://www.techloyce.com',
    'images': [
        'static/description/banner.gif',
    ],
    'depends': ['sale_management', 'crm'],
    'price': 400,
    'currency': 'EUR',
    'license': 'OPL-1',

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/schedule.xml',
    ],
    'installable': True,
    'application': True,
}
