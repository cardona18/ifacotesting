# -*- coding: utf-8 -*-
{
    'name': "Integración RSP - ADMIN",

    'summary': """
    Permisos para dar de alta empleados
    en los grupos de reclutamiento y selección.
    """,

    'description': """

    """,

    'author': "IACDev (iacdev@grupoifaco.com.mx)",
    'website': "http://www.grupoifaco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_recruitment_gi','hr_paysheet'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml'
    ]
}
