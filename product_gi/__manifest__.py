# -*- coding: utf-8 -*-
{
    'name': "PRODUCT GI",

    'summary': """""",

    'description': """

    """,

    'author': "Omar Torres",
    'website': "www.grupoifaco.com",

    # Categories can be used to filter modules in modules listing
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product','sale'],

    # always loaded
    'data': [
        # 'views/product_gi_main.xml',
        'views/product_sanitary_registration.xml',
        'views/product_lgsa226.xml',
        'views/product_lgsa229.xml',
        'views/product_pharm_form.xml',
        'views/product_template.xml'
    ]
}
