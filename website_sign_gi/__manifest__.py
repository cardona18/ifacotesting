# -*- coding: utf-8 -*-
{
    'name': "Sign GI",

    'summary': """Adecuación al módulo de Sign para control de los documentos que cada usuario puede ver""",

    'description': """

    """,

    'author': "Mateo Alexander Zabala Gutierrez (mzabalagutierrez@gmail.com)",
    'website': "https://www.grupoifaco.com.mx/",

    # Categories can be used to filter modules in modules listing
    'category': 'Document Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website_sign'],

    # always loaded
    'data': [
        'security/security.xml'
    ]
}
