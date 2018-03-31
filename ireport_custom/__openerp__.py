# -*- coding: utf-8 -*-
{
    'name': "IREPORT CUSTOM",

    'summary': "Adaptación de la libreria IReport en ODOO",

    'description': """

    """,

    'author': "IACDev (iacdev@grupoifaco.com.mx)",
    'website': "http://www.grupoifaco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Base',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        'views/ireport_custom_main.xml',
        'views/ireport_report.xml',
    ]
}
