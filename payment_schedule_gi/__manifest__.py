# -*- coding: utf-8 -*-
{
    'name': "Programación de pagos",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.odoo.com
        
        """,

    'description': """

    """,

    'author': "",
    'website': "",

    # Categories can be used to filter modules in modules listing
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/account_invoice.xml',
    ]
}
