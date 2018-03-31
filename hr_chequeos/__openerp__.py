# -*- coding: utf-8 -*-
{
    'name': "HR CHEQUEOS",

    'summary': """Administración de tiempo trabajado""",

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
    'depends': ['base','hr', 'hr_paysheet'],

    # always loaded
    'data': [
      # 'security/security.xml',
      'security/ir.model.access.csv',
      'wizards/hr_worktime_wizard.xml',
      'wizards/hr_assign_period_wizard.xml',
      'wizards/hr_timecheck_fix_wizard.xml',
      'views/hr_chequeos_main.xml',
      'views/hr_timecheck_turn.xml',
      'views/hr_timecheck_node.xml',
      'views/hr_fingerprint.xml',
      'views/hr_employee.xml',
      'views/hr_timecheck_workday.xml',
      'templates/timecheck_monitor.xml',
      'views/hr_work_period.xml',
      'views/hr_time_checkout.xml',
      'views/hr_timefix_log.xml',
    ]
}