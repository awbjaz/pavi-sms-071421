# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB HR Expense",

    'summary': """
        HR Expense.
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '13.0.1.2.0',

    'depends': ['hr_expense'],

    'data': [
        'data/hr_expense_generated_num_sequence.xml',
        'views/hr_expense_view_form.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False

}
