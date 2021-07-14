# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "Streamtech Modules Pack",
    'summary': """
        StreamTech Specific Modules Pack.
        """,
    'description': """
        Created to serve as the single module to trigger (install/upgrade) the inclusion of AWB modules and their dependencies.
    """,
    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",
    'category': 'Initialization',
    'version': '13.0.1.0.0',
    'depends': [
        'account_analytic_parent',
        'awb_account_aging_reports',
        'awb_account_consolidation',
        'awb_account_groups',
        'awb_account_je_approval',
        'awb_account_lockdate',
        'awb_account_move_batch',
        'awb_asset_depreciation',
        'awb_asset_project',
        'awb_asset_updates',
        'awb_bill_pre_termination',
        'awb_cashflow_compare',
        'awb_coa_approval',
        'awb_cost_allocation',
        'awb_counter_receipt',
        'awb_hr_expense',
        'awb_hr_expense_approval',
        'awb_operational_costing',
        'awb_overage_receiving',
        'awb_payment_analytic_account',
        'awb_payment_internal_transfer',
        'awb_product_unique',
        'awb_purchase_discount',
        'awb_purchase_order_approval',
        'awb_report_header',
        'awb_subscriber_bill',
        'awb_subscriber_bill_automation',
        'awb_subscriber_location',
        'awb_subscriber_product_information',
        'awb_vendor_credit_limit',
        'contact_record',
        'portal_partner_data_no_edit',
        'requisition_approval',
        'requisition_material',
        'requisition_purchase',
        'salesforce_connector',
        'sequence_reset_period',
        'streamtech_account_reports',
        'streamtech_journal_voucher',
        'streamtech_or_print',
        'streamtech_salesforce_connector',
    ],
    'data': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
