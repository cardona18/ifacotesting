# -*- coding: utf-8 -*-
{
    'name': "Fecha de fabricación",

    'summary': """""",

    'description': """

    """,

    'author': "Omar Torres",
    'website': "",

    # Categories can be used to filter modules in modules listing
    'category': 'Warehouse',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock','quality_manager_gi'],

    # always loaded
    'data': [
        'views/stock_production_lot.xml'
    ]
}


