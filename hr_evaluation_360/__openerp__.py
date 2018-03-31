# -*- coding: utf-8 -*-
{
    'name': "hr_evaluation_360",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Grupo Ifaco",
    'website': "http://www.grupoifaco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr','website', 'hr_recruitment_gi'],

    'aplication': True,

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_evaluation_360.xml',
        'views/hr_evaluation_questions.xml',
        'views/ev_hr_job.xml',
        'views/hr_evaluation_competences.xml',
        'views/hr_plan_evaluation.xml',
        'views/hr_comp_points.xml',
        'views/admin_answers.xml',
        'views/hr_states_eval.xml',
        'views/answered_evaluation.xml',
        'views/hr_general_quest_360.xml',
        'views/commentary_360.xml',
        'views/template/send_evaluation.xml',
        'views/web/report_general.xml',
        'views/web/select_report.xml',
        'views/web/evaluations360.xml',
        'views/web/my_reports.xml',
    ],
}