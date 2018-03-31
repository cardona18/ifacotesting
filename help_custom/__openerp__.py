# -*- coding: utf-8 -*-
{
    'name': "Manuales de usuario",

    'summary': """
        Soporte para manuales de usuario
    """,

    'description': """

    """,

    'author': "IACDev (iacdev@grupoifaco.com.mx)",
    'website': "http://www.grupoifaco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sistemas',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/help_custom_main.xml',
        'views/menu_help.xml',
        'views/help_user_manual.xml'
    ],
    # Qweb templates
    'qweb': [
        'templates/user_menu.xml'
    ]
}
