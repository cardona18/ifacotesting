# -*- coding: utf-8 -*-
{
    'name': "QUALITY MANAGER GI",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.odoo.com""",

    'description': """
        Se debe de activar el seguimiento por lotes y fecha de caducidad 
    """,

    'author': "",
    'website': "",

    # Categories can be used to filter modules in modules listing
    'category': 'Uncategorized',
    'version': '11.1.1',

    # any module necessary for this one to work correctly
    'depends': ['base','quality','hr','quality_mrp','product','stock'],

    # always loaded
    'data': [
        'views/quality_point.xml',
        'views/quality_check_view_form_small_gi.xml',
        'views/stock_production_lot.xml',
        'views/product_template.xml',
        'views/hr_employee.xml',
        'views/quality_check.xml',
        'views/stock_move_line.xml',
    ]
}
