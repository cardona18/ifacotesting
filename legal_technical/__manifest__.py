# -*- coding: utf-8 -*-
{
    'name': "Técnico Legal",

    'summary': """""",

    'description': """

    """,

    'author': "Omar Torres",
    'website': "http://www.grupoifaco.com",

    # Categories can be used to filter modules in modules listing
    'category': 'Técnico Legal',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product_gi'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/legal_technical_main.xml'
    ],
    'application':  True
}
