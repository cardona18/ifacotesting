# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
import logging
import urllib

from openerp import fields, models, api

_logger = logging.getLogger(__name__)

class hr_ptu_wizard(models.TransientModel):
    _name = 'hr.ptu.wizard'
    _description = 'HR PTU WIZARD'

    def _default_year_id(self):
        return self.env['hr.paysheet.year'].sudo().search([('name', '=', datetime.today().date().year - 1)], limit=1).id

    gen_type = fields.Selection(
        string='Tipo',
        size=2,
        default='PR',
        selection=[
            ('PR', 'Proyección'),
            ('CA', 'Cálculo')
        ]
    )
    export_type = fields.Selection(
        string='Exportar',
        size=4,
        default='PREV',
        selection=[
            ('PREV', 'Vista previa'),
            ('SHEE', 'Hoja de cálculo'),
            ('REPO', 'Reporte'),
            ('EXPO', 'Exportar a la nómina'),
        ]
    )
    company_ids = fields.Many2many(
        string='Empresas',
        comodel_name='res.company'
    )
    company_amount_ids = fields.One2many(
        string='Empresas',
        comodel_name='hr.ptu.company.line',
        inverse_name='wizard_id'
    )
    year_id = fields.Many2one(
        string='Ejercicio',
        comodel_name='hr.paysheet.year',
        default=_default_year_id
    )
    active_days = fields.Integer(
        string='D.T. empleados activos',
        default=1,
        help='Mínimo de días trabajados para considerar a los empleados activos'
    )
    inactive_days = fields.Integer(
        string='D.T. empleados inactivos',
        default=60,
        help='Mínimo de días trabajados para considerar a los empleados inactivos'
    )
    inactive_employees = fields.Boolean(
        string='Mostrar inactivos',
        default=True
    )

    @api.multi
    def ptu_preview(self):

        self.env['hr.ptu.line'].search([('wizard_id', '=', self.id)]).unlink()

        if self.gen_type == 'PR':

            for company_id in self.company_ids:

                self.env.cr.execute("""
                    SELECT * FROM (
                        SELECT employee_id, SUM(pt.amount) AS amount
                        FROM hr_paysheet_trade pt
                        INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
                        INNER JOIN hr_employee he ON ps.employee_id = he.id
                        INNER JOIN resource_resource rr ON he.resource_id = rr.id
                        INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                        WHERE pt.year_id = %s AND rr.company_id = %s AND pc.code IN (34,36,65,39) %s
                        GROUP BY employee_id
                    ) AS fq WHERE amount > 0
                """ % (self.year_id.id, company_id.id, '' if self.inactive_employees else 'AND rr.active = TRUE'))

                for employee_id in self.env['hr.employee'].search([('id', 'in', [row[0] for row in self.env.cr.fetchall()]), '|', ('active','=',True), ('active','=',False)]):

                    if employee_id.ignore_bp:
                        _logger.debug("IGNORE BP: %s", employee_id.name)
                        continue

                    contract_id = self.env['hr.contract'].search([
                        ('employee_id', '=', employee_id.id),
                        ('for_paysheet', '=', True),
                        '|',
                        ('active','=',True),
                        ('active','=',False)
                    ], limit=1)

                    if not contract_id:
                        _logger.debug("NO CONTRACT: %s", employee_id.name)
                        continue

                    self.env.cr.execute("""
                        SELECT COALESCE(SUM(pt.amount), 0)
                        FROM hr_paysheet_trade pt
                        INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
                        INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                        WHERE pt.year_id = %s AND ps.employee_id = %s AND pc.code IN (34)
                    """ % (self.year_id.id, employee_id.id))

                    worked_days = self.env.cr.fetchone()[0]

                    self.env.cr.execute("""
                        SELECT COALESCE(SUM(pt.amount), 0)
                        FROM hr_paysheet_trade pt
                        INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
                        INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                        WHERE pt.year_id = %s AND ps.employee_id = %s AND pc.code IN (36,65)
                    """ % (self.year_id.id, employee_id.id))

                    worked_days += self.env.cr.fetchone()[0] * 7 / 6

                    self.env.cr.execute("""
                        SELECT COALESCE(SUM(pt.amount), 0)
                        FROM hr_paysheet_trade pt
                        INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
                        INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                        WHERE pt.year_id = %s AND ps.employee_id = %s AND pc.code IN (39)
                    """ % (self.year_id.id, employee_id.id))

                    worked_days += self.env.cr.fetchone()[0]

                    raw_worked_days = worked_days
                    worked_days = min(worked_days, self.year_id.get_days())
                    ptu_days = contract_id.find_benefit(14)
                    pantry = contract_id.find_benefit(15)
                    pantry = pantry.amount / (365 / 12.0) if pantry else 0
                    wage = contract_id.wage

                    ptu = ((wage + pantry) * (ptu_days.amount if ptu_days else 0)) * (worked_days / self.year_id.get_days())

                    if ptu == 0:
                        _logger.debug("EMP: %s, WAGE: %s, PANTRY: %s, PTU_DAYS: %s, WD: %s, MAX_WD: %s, RAW_WD: %s", employee_id.name, wage, pantry, (ptu_days.amount if ptu_days else 0), worked_days, self.year_id.get_days(), raw_worked_days)

                    # Retrieve paid PTU

                    current_year = self.year_id.search([('name', '=', int(self.year_id.name) +  1)], limit=1)
                    ptu_amount = 0

                    if current_year.id:

                        self.env.cr.execute("""
                            SELECT COALESCE(SUM(ABS(pt.amount)), 0)
                            FROM hr_paysheet_trade pt
                            INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
                            INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                            WHERE pt.year_id = %s AND ps.employee_id = %s AND pc.code IN (14)
                        """ % (current_year.id, employee_id.id))

                        ptu_amount += self.env.cr.fetchone()[0]

                    self.env['hr.ptu.line'].create({
                        'wizard_id': self.id,
                        'employee_id': employee_id.id,
                        'wage': contract_id.wage,
                        'ptu_amount': ptu_amount,
                        'amount': ptu,
                        'worked_days': worked_days,
                        'ptu_days': ptu_days.amount if ptu_days else 0,
                        'daily_pantry': pantry
                    })

            if self.export_type in ('SHEE','PREV'):

                return {
                    'type' : 'ir.actions.act_url',
                    'url': '/web/reports/hr_ptu_report?wizard_id=%s&export_type=%s&type=%s' % (self.id, self.export_type, self.gen_type),
                    'target': 'new' if self.export_type == 'PREV' else 'self',
                }

            else:

                self.env.cr.commit()

                report = self.env['ireport.report'].sudo().search([('code','=','PTU_PROYECTADO')], limit=1)
                out_name = 'PROYECCION_PTU'

                parameters = {
                    'current_year': self.year_id.name,
                    'wizard_id': self.id,
                    'out_name': out_name
                }

                report.setParameters(parameters)

                report_file  = report.build()
                report_file += '/%s.pdf' % out_name

                return {
                    'type' : 'ir.actions.act_url',
                    'url': '/web/ireport/download_manager?path=%s&type=%s' % (urllib.quote_plus(report_file), 'pdf'),
                    'target': 'new'
                }

        if self.gen_type == 'CA':

            month_days = 30.416667

            for line in self.company_amount_ids:

                wd_total = 0
                wage_total = 0
                lu_wages = {}

                # GET WAGE LIMIT
                contract_id = self.env['hr.contract'].search([
                    ('employee_id', '=', line.employee_id.id),
                    ('for_paysheet', '=', True),
                    '|',
                    ('active', '=', True),
                    ('active', '=', False)
                ], limit=1)

                if not contract_id:
                    _logger.debug("LIMIT EMPLOYEE CONTRACT NOT FOUND: %s", line.employee_id.id)
                    continue

                limit_wage = self.get_last_wage(contract_id, self.year_id)
                max_emp_wage = limit_wage * 1.2
                max_wage  = max_emp_wage * self.year_id.get_days()


                # ACTIVE EMPLOYEES

                self.env.cr.execute("""
                    SELECT * FROM (
                        SELECT employee_id, SUM(pt.amount) AS amount
                        FROM hr_paysheet_trade pt
                        INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
                        INNER JOIN hr_employee he ON ps.employee_id = he.id
                        INNER JOIN resource_resource rr ON he.resource_id = rr.id
                        INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                        WHERE pt.year_id = %s AND rr.company_id = %s
                        AND (he.manager = FALSE OR he.manager IS NULL)
                        AND rr.active = TRUE AND (he.ignore_ptu = FALSE OR he.ignore_ptu IS NULL) AND pc.code IN (34,36,65,39)
                        GROUP BY employee_id
                    ) AS fq WHERE amount >= %s
                """ % (self.year_id.id, line.company_id.id, self.active_days))

                for employee in self.env['hr.employee'].browse([row[0] for row in self.env.cr.fetchall()]):

                    if employee.ignore_ptu:
                        continue

                    contract_id = self.env['hr.contract'].search([
                        ('employee_id', '=', employee.id),
                        ('for_paysheet', '=', True)
                    ], limit=1)

                    if not contract_id:
                        continue

                    # EMPLOYEE LAST WAGE
                    base_wage = self.get_last_wage(contract_id, self.year_id)
                    last_wage = min(max_emp_wage, base_wage)

                    # EMPLOYEE WORKED DAYS

                    self.env.cr.execute("""
                        SELECT COALESCE(SUM(pt.amount), 0)
                        FROM hr_paysheet_trade pt
                        INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
                        INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                        WHERE pt.year_id = %s AND ps.employee_id = %s AND pc.code IN (34,39)
                    """ % (self.year_id.id, employee.id))

                    worked_days = self.env.cr.fetchone()[0]

                    self.env.cr.execute("""
                        SELECT COALESCE(SUM(pt.amount), 0)
                        FROM hr_paysheet_trade pt
                        INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
                        INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                        WHERE pt.year_id = %s AND ps.employee_id = %s AND pc.code IN (36,65)
                    """ % (self.year_id.id, employee.id))

                    worked_days += self.env.cr.fetchone()[0] * 7 / 6
                    worked_days = min(worked_days, self.year_id.get_days())

                    wd_total += worked_days

                    # EMPLOYEE WAGE

                    wage_amount = last_wage * worked_days

                    # CHECK EMPLOYEE WAGE LIMIT

                    emp_wage_limit = 0

                    if not line.company_id.has_ptu:
                        emp_wage_limit = base_wage * month_days

                    self.env['hr.ptu.line'].create({
                        'wizard_id': self.id,
                        'employee_id': employee.id,
                        'base_wage': base_wage,
                        'wage': wage_amount,
                        'worked_days': worked_days,
                        'last_wage': last_wage,
                        'month_wage': emp_wage_limit,
                        'company_line_id': line.id
                    })

                # INACTIVE EMPLOYEES

                self.env.cr.execute("""
                    SELECT * FROM (
                        SELECT employee_id, SUM(pt.amount) AS amount
                        FROM hr_paysheet_trade pt
                        INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
                        INNER JOIN hr_employee he ON ps.employee_id = he.id
                        INNER JOIN resource_resource rr ON he.resource_id = rr.id
                        INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                        WHERE pt.year_id = %s AND rr.company_id = %s
                        AND (he.manager = FALSE OR he.manager IS NULL)
                        AND (he.ignore_ptu = FALSE OR he.ignore_ptu IS NULL)
                        AND rr.active = FALSE AND pc.code IN (34,36,65,39)
                        GROUP BY employee_id
                    ) AS fq WHERE amount >= %s
                """ % (self.year_id.id, line.company_id.id, self.inactive_days))

                for employee in self.env['hr.employee'].browse([row[0] for row in self.env.cr.fetchall()]):

                    if employee.ignore_ptu:
                        continue

                    contract_id = self.env['hr.contract'].search([
                        ('employee_id', '=', employee.id),
                        ('for_paysheet', '=', True),
                        ('active', '=', False)
                    ], limit=1)

                    if not contract_id:
                        continue

                    # EMPLOYEE LAST WAGE
                    base_wage = self.get_last_wage(contract_id, self.year_id)
                    last_wage = min(max_emp_wage, base_wage)

                    # EMPLOYEE WORKED DAYS

                    self.env.cr.execute("""
                        SELECT COALESCE(SUM(pt.amount), 0)
                        FROM hr_paysheet_trade pt
                        INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
                        INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                        WHERE pt.year_id = %s AND ps.employee_id = %s AND pc.code IN (34,39)
                    """ % (self.year_id.id, employee.id))

                    worked_days = self.env.cr.fetchone()[0]

                    self.env.cr.execute("""
                        SELECT COALESCE(SUM(pt.amount), 0)
                        FROM hr_paysheet_trade pt
                        INNER JOIN hr_paysheet ps ON pt.paysheet_id = ps.id
                        INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                        WHERE pt.year_id = %s AND ps.employee_id = %s AND pc.code IN (36,65)
                    """ % (self.year_id.id, employee.id))

                    worked_days += self.env.cr.fetchone()[0] * 7 / 6
                    worked_days = min(worked_days, self.year_id.get_days())

                    wd_total += worked_days

                    # EMPLOYEE WAGE

                    wage_amount = last_wage * worked_days

                    # CHECK EMPLOYEE WAGE LIMIT

                    emp_wage_limit = 0

                    if not line.company_id.has_ptu:
                        emp_wage_limit = base_wage * month_days

                    self.env['hr.ptu.line'].create({
                        'wizard_id': self.id,
                        'employee_id': employee.id,
                        'base_wage': base_wage,
                        'wage': wage_amount,
                        'worked_days': worked_days,
                        'last_wage': last_wage,
                        'month_wage': emp_wage_limit,
                        'company_line_id': line.id
                    })

                # CHECK WAGE LIMITS
                for emp_line in line.emp_line_ids:

                    emp_line.wage_limit = max_wage
                    emp_line.has_max_wage = emp_line.employee_id.id == line.employee_id.id

                    emp_wage = min(emp_line.wage_limit, emp_line.wage)
                    wage_total += emp_wage
                    emp_line.wage = emp_wage

                # CALC FACTORS
                line.wage_sum = wage_total
                line.wd_sum = wd_total
                line.wage_factor = (line.amount / 2.0) / wage_total
                line.wd_factor = (line.amount / 2.0) / wd_total

                # CALC EMPLOYEE PAYMENTS
                for emp_line in line.emp_line_ids:
                    emp_line.wage_ptu = emp_line.wage * line.wage_factor
                    emp_line.wd_ptu = emp_line.worked_days * line.wd_factor


            if self.export_type in ('SHEE','PREV','EXPO'):

                return {
                    'type' : 'ir.actions.act_url',
                    'url': '/web/reports/hr_ptu_report?wizard_id=%s&export_type=%s&type=%s' % (self.id, self.export_type, self.gen_type),
                    'target': 'new' if self.export_type == 'PREV' else 'self',
                }

            else:

                self.env.cr.commit()

                report = self.env['ireport.report'].sudo().search([('code','=','CALCULO_PTU')], limit=1)
                out_name = 'CALCULO_PTU'

                parameters = {
                    'current_year': self.year_id.name,
                    'wizard_id': self.id,
                    'out_name': out_name
                }

                report.setParameters(parameters)

                report_file  = report.build()
                report_file += '/%s.pdf' % out_name

                return {
                    'type' : 'ir.actions.act_url',
                    'url': '/web/ireport/download_manager?path=%s&type=%s' % (urllib.quote_plus(report_file), 'pdf'),
                    'target': 'new'
                }


    def get_last_wage(self, contract, _year):

        last_sc = self.env['hr.salary.change'].search([
            ('contract_id', '=', contract.id),
            ('move_date', '>=', _year.from_date),
            ('move_date', '<=', _year.to_date)
        ], limit=1, order='move_date DESC')

        if last_sc:
            return last_sc.old_salary

        next_year = self.env['hr.paysheet.year'].search([('name', '=', int(_year.name) + 1)], limit=1)

        if not next_year:
            return contract.wage

        last_sc = self.env['hr.salary.change'].search([
            ('contract_id', '=', contract.id),
            ('move_date', '>=', next_year.from_date),
            ('move_date', '<=', next_year.to_date)
        ], limit=1, order='move_date ASC')

        if last_sc:
            return last_sc.old_salary

        return contract.wage
