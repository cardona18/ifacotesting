# -*- coding: utf-8 -*-
{
    'name': "RECLUTAMIENTO Y SELECCIÓN GI",

    'summary': """Adecuaciones al módulo de reclutamiento para la funcionalidad interna""",

    'description': """""",

    'author': "IACDev (iacdev@grupoifaco.com.mx)",
    'website': "http://www.grupoifaco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr', 'hr_recruitment'],

    # always loaded
    'data': [
        'security/security.xml',
        #'security/ir.model.access.csv',
        'views/hr_job_gi.xml',
        #'views/hr_publish_job_gi.xml',
        'views/hr_applicant_gi.xml', 
        'views/hr_employee_gi.xml',
        'views/hr_department_gi.xml',
        'views/templates/hr_recruiment_mails.xml',
        'views/hr_aprov_aplicant.xml',
        'views/hr_employee_request.xml',
        'views/hr_publish_job_web.xml',
    ]
}
