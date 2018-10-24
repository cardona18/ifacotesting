# -*- coding: utf-8 -*-
{
    'name': "Rutas Email",

    'summary': """
        Permite dirigir el servidor de salida de un email según su dominio
    """,

    'description': """

    """,

    'author': "Omar Torres Silva (otorresgi18@gmail.com)",
    'website': "http://www.grupoifaco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Social Network',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/mail_domain_route.xml',
    ]
}
