# -*- coding: utf-8 -*-
{
    'name': "IREPORT CUSTOM",

    'summary': "Adaptación de la libreria IReport en ODOO",

    'description': """

    """,

    'author': "IACDev (iacdev@grupoifaco.com.mx)",
    'website': "http://www.grupoifaco.com",
    'category': 'Base',
    'version': '5.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        'views/ireport_custom_main.xml',
        'views/ireport_report.xml',
        'views/ireport_web_templates.xml',
    ]
}
