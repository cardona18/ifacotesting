# -*- coding: utf-8 -*-
{
    'name': "Organigrama",

    'summary': """
        """,

    'description': """
       Genera un organigrama de forma jerárquica 
    """,

    'author': "IACDev (iacdev@grupoifaco.com.mx)",
    'website': "http://www.grupoifaco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_recruitment_gi'],

    # always loaded
    'data': [
        'views/web/hr_org_char_main.xml',
        'views/hr_job_org.xml',
        'views/hr_employee.xml',
    ]
}
