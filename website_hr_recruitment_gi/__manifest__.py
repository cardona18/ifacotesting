# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Bolsa de trabajo',
    'category': 'Website',
    'version': '1.0',
    'summary': 'Bolsa de trabajo',
    'description': """
Odoo Contact Form
====================

        """,
    'depends': ['website_partner', 'hr_recruitment', 'website_mail', 'website_form','hr_recruitment_gi'],
    'data': [
        'security/ir.model.access.csv',
        'security/website_hr_recruitment_security.xml',
        'data/config_data.xml',
        'views/website_hr_recruitment_templates.xml',
        'views/hr_recruitment_views.xml',
        'views/hr_job.xml',
        'views/hr_applicant_gi_web.xml',
    ],
    'demo': [
        'data/hr_job_demo.xml',
    ],
    'installable': True,
}
