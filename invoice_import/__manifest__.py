# -*- coding: utf-8 -*-
{
    'name': "Importar facturas SIAGI",

    'summary': """""",

    'description': """""",

    'author': "OMAR TORRES (otorresgi18@gmail.com)",
    'website': "http://www.grupoifaco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting & Finance',
    'version': '0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web','l10n_mx_edi','mrp','mssql_proxy','sale'],

    # always loaded
    'data': [
        'views/invoice_import_main.xml',
        'wizards/siagi_invoice_wizard.xml',
        'views/account_invoice.xml',
        #'views/account_invoice_report.xml',
        'views/cfdiv33_report.xml',
        #'views/res_config_settings_views.xml',
        'views/ir_conf_sqlserver.xml',
        'views/account_payment.xml',
        'views/stock_picking_type.xml', 
        #'views/account_register_payments.xml',
    ]
}
