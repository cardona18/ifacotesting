# -*- coding: utf-8 -*-
{
    'name': "HR PAYSHEET",

    'summary': """
    Adecuaciones a la nómina para Grupo IFACO""",

    'description': """
    """,

    'author': "IACDev (iacdev@grupoifaco.com.mx)",
    'website': "http://www.grupoifaco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['hr','hr_contract','account','gi_base','cfdi_base','data_filemanager','ireport_custom', 'fleet'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_paysheet_main.xml',
        'report/hr_paysheet_report.xml',
        'report/hr_wage_report.xml',
        'reports/cfdi_print_report.xml',
        'reports/paysheet_council_report.xml',
        'reports/paysheet_voucher_report.xml',
        'wizards/hr_employee_leave.xml',
        'wizards/hr_lot_report_wizard.xml',
        'wizards/hr_salary_change_wizard.xml',
        'wizards/hr_sdi_calc.xml',
        'wizards/hr_sua_file_wizard.xml',
        'wizards/hr_employee_wage_wizard.xml',
        'wizards/hr_medical_insurance_wizard.xml',
        'wizards/hr_ptu_wizard.xml',
        'wizards/hr_export_rfc_wizard.xml',
        'wizards/hr_beneficiary_wizard.xml',
        'wizards/hr_retention_wizard.xml',
        'wizards/hr_import_concepts_wizard.xml',
        'wizards/hr_paysheet_lot_wizard.xml',
        'wizards/hr_cfdi_mail_wizard.xml',
        'wizards/hr_paysheet_cfdi_wizard.xml',
        'wizards/hr_cfdi_cancel_wizard.xml',
        'wizards/hr_gen_xml_wizard.xml',
        'views/hr_absence.xml',
        'views/hr_academic_institution.xml',
        'views/hr_academic_level.xml',
        'views/hr_account_expense.xml',
        'views/hr_business_segment.xml',
        'views/hr_contract.xml',
        'views/hr_contract.xml',
        'views/hr_contract_regime.xml',
        ## NO ORDENAR ##
        'views/hr_council_voucher.xml',
        'views/hr_council_lot.xml',
        ## NO ORDENAR ##
        'views/hr_council_member.xml',
        'views/hr_employee.xml',
        'views/hr_employer_registration.xml',
        'views/hr_leave.xml',
        'views/hr_old_policy_conf.xml',
        'views/hr_paysheet.xml',
        'views/hr_paysheet_category.xml',
        'views/hr_paysheet_concept.xml',
        'views/hr_paysheet_benefit.xml',
        'views/hr_paysheet_lot.xml',
        'views/hr_paysheet_rule.xml',
        'views/hr_paysheet_sat_concept.xml',
        'views/hr_paysheet_struct.xml',
        'views/hr_paysheet_year.xml',
        'views/hr_periodic_payment.xml',
        'views/hr_policy_config.xml',
        'views/hr_profession.xml',
        'views/hr_rank_row.xml',
        'views/hr_rank_table.xml',
        'views/hr_ss_move.xml',
        'views/hr_study_title.xml',
        'views/hr_work_risk.xml',
        'views/hr_xml_cfdi.xml',
        ## NO ORDENAR ##
        'views/hr_account_access.xml',
        ## NO ORDENAR ##
        'views/hr_salary_change.xml',
        'views/res_company.xml',
        'views/res_country.xml',
        'views/hr_time_checker_config.xml',
        'views/hr_medical_insurance.xml',
        'views/hr_year_bonus.xml',
        'views/hr_holidays_line.xml',
        'views/hr_ptu_line.xml',
        'views/hr_sua_state.xml',
        'views/hr_holidays_request.xml',
        'views/hr_leave_request.xml',
        'views/hr_public_holiday.xml',
        'views/hr_public_holiday_category.xml',
        'views/hr_company_change.xml',
        'views/hr_department.xml',
        'views/hr_policy_line.xml',
        'views/hr_extra_time_request.xml',
        'views/hr_paysheet_month.xml',
        'data/hr.sua.state.csv',
        'tasks/hr_holidays_update_task.xml',
        'templates/mail_templates.xml',
        'templates/hr_request_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}