# -*- coding: utf-8 -*-
{
    'name': "GI BASE",

    'summary': """
        Modificaciones globales al sistema""",

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
    'depends': ['hr','base'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/gi_base_main.xml',
        'views/res_company.xml',
        'views/res_country_city.xml',
        'views/res_country_state.xml'
    ]
}
