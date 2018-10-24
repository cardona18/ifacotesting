# -*- coding: utf-8 -*-
{
    'name': "Solicitudes",

    'summary': """Sistema base para solicitudes y aprobaciones""",

    'description': """

    """,

    'author': "Omar Torres",
    'website': "http://www.grupoifaco.com",

    # Categories can be used to filter modules in modules listing
    'category': 'Solicitudes',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/requests_gi_main.xml',
        'views/res_partner.xml',
    ]
}
