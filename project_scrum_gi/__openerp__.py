# -*- coding: utf-8 -*-
{
    'name': "SCRUM GI",

    'summary': """METODOLOGÍA SCRUM GRUPO IFACO""",

    'description': """

    """,

    'author': "Omar Torres Silva",
    'website': "http://www.grupoifaco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Project Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','project', 'project_issue'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/project_scrum_gi_main.xml',
        'wizards/project_scrum_monitor_wizard.xml',
    	'views/project_task.xml',
        'views/project_issue.xml',
        'views/project_scrum_us.xml',
        'views/project_scrum_sprint.xml',
        'templates/project_scrum_web.xml',
    ]
}
