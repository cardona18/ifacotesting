# -*- coding: utf-8 -*-
{
    'name': "ACCOUNT GI",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.odoo.com""",

    'description': """

    """,

    'author': "",
    'website': "",

    # Categories can be used to filter modules in modules listing
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_reports','account_cancel','partner_credit_limit','contacts','product','l10n_mx_edi','currency_rate_live'],
    'application': False,

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizards/cancel_account_invoice.xml',
        'wizards/account_common_report_view.xml',
        'report/account_report_payment_receipt.xml',
        'views/account_invoice.xml',
        'views/partner_view.xml',
        'views/account_report_partnerledger.xml',
        'views/account_report_trialbalance.xml',
        'views/account_register_payments.xml',
        'views/res_partner.xml',
        'views/payment10.xml',
        'views/account_payment_from_invoices.xml'
    ]
}
