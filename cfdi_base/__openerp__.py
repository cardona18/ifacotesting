# -*- coding: utf-8 -*-
{
    'name': "Base para timbrado CFDI",

    'summary': """
    Configuraciones básicas para tambrado CFDI
    """,

    'description': """

    """,

    'author': "IACDev (iacdev@grupoifaco.com.mx)",
    'website': "http://www.grupoifaco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','gi_base'],

    # always loaded
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        'views/cfdi_base_main.xml',
        'views/cfdi_server_config.xml',
        'views/res_bank.xml',
        'views/res_company.xml',
        'views/cfdi_town.xml',
        'views/cfdi_financial_regime.xml'
    ]
}
