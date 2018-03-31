# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from dateutil import tz
import calendar
import locale
import logging
import os
import subprocess
import sys
import urllib
import uuid

from openerp import fields, models, api
from odoo.exceptions import UserError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)

class hr_sua_file_wizard(models.TransientModel):
    _name = 'hr.sua.file.wizard'
    _description = 'HR SUA FILE WIZARD'

    file_type = fields.Selection(
        string='Exportar',
        selection=[
            ('01', 'Acumulados de 2%'),
            ('02', 'Catalogo de Empleados'),
            ('03', 'Trabajadores SUA'),
            ('04', 'Movimientos afiliatorios SUA'),
            ('05', 'Incapacidades'),
            ('06', 'IDSE Bimestral'),
            ('07', 'Crédito Infonavit'),
            ('08', 'Datos afiliatorios')
        ]
    )
    from_date = fields.Date(
        string='Desde'
    )
    to_date = fields.Date(
        string='Hasta'
    )
    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company'
    )
    employer_id = fields.Many2one(
        string='Registro patronal',
        comodel_name='hr.employer.registration'
    )
    employer_place = fields.Char(
        string='Domicilio del patrón',
        related='employer_id.place'
    )
    all_employees = fields.Boolean(
        string='Todos los empleados'
    )

    # BASE PHP COMMAND
    _BASE_COMMAND = 'php /opt/php_files'

    @api.multi
    def generate_file(self):
        """
        Generate selected report / file
        """

        # LOAD SYSTEM TIMEZONE
        os.environ['TZ'] = "America/Mexico_City"

        if self.file_type == '01':

            report = self.env['ireport.report'].sudo().search([('code','=','2PER_MONTH_REPORT')], limit=1)
            current_date = datetime.today()
            out_name = 'AC_%s' % self.company_id.short_name

            parameters = {
                'company_id': self.company_id.id,
                'company_name': self.company_id.name,
                'report_month': self.locale_format(datetime.strptime(self.from_date, DEFAULT_SERVER_DATE_FORMAT), '%B/%Y', True, 0),
                'from_date': self.from_date,
                'to_date': self.to_date,
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

        if self.file_type == '02':

            report = self.env['ireport.report'].sudo().search([('code','=','2PER_EMPLOYEES')], limit=1)
            current_date = datetime.today()
            out_name = 'EMP_%s' % self.company_id.short_name

            parameters = {
                'company_id': self.company_id.id,
                'company_name': self.company_id.name,
                'report_month': self.locale_format(datetime.strptime(self.to_date, DEFAULT_SERVER_DATE_FORMAT), '%d DE %B DE %Y').upper(),
                'from_date': self.from_date,
                'to_date': self.to_date,
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

        # CHANGE DEAFULT ENCODING
        reload(sys)
        sys.setdefaultencoding('utf-8')

        if self.file_type == '03':

            from_date = datetime.strptime(self.from_date, DEFAULT_SERVER_DATE_FORMAT)
            to_date = datetime.strptime(self.to_date, DEFAULT_SERVER_DATE_FORMAT)
            out_path = '/tmp/odoo_txt/%s' % uuid.uuid4()
            filename = '%s/employee_data.txt' % out_path
            file_encoded = '%s/employee_data_encoded.txt' % out_path
            txt_content = ''
            emp_filter = [('employer_registration', '=', self.employer_id.id)]

            if not self.all_employees:
                emp_filter.append(('ss_in_date','>=', self.from_date))
                emp_filter.append(('ss_in_date','<=', self.to_date))

            emp_filter.append('|')
            emp_filter.append(('active', '=',True))
            emp_filter.append(('active', '=', False))

            employees = self.env['hr.employee'].search(emp_filter, order="old_id")

            if not len(employees):
                raise UserError('No se encontraron registros')

            for employee in employees:

                in_date = datetime.strptime(employee.in_date, DEFAULT_SERVER_DATE_FORMAT)
                ss_in_date = datetime.strptime(employee.ss_in_date, DEFAULT_SERVER_DATE_FORMAT)
                min_in_date = ss_in_date.replace(day=30, month=6, year=1997)
                contract = self.env['hr.contract'].search([
                    ('employee_id','=',employee.id),
                    ('for_paysheet','=',True),
                    '|',
                    ('active', '=',True),
                    ('active', '=',False)
                ], limit=1)

                if not contract:
                    _logger.info("SIN CONTRATO - %s" % (employee.name_related))
                    continue

                first_sc = self.env['hr.salary.change'].search([
                    ('contract_id', '=', contract.id),
                    ('move_date','>=', self.from_date),
                    ('move_date','<=', self.to_date)
                ], order = 'id DESC', limit=1)

                first_wage = first_sc.old_sdi if first_sc.id else 0

                txt_content += '%s%s%s%s%s%s%s%s%s%s%s%s%s%s\r\n' % (
                    employee.employer_registration.name,
                    employee.ssn,
                    employee.rfc,
                    employee.curp,
                    employee.sua_name[:50].ljust(50),
                    employee.worker_type,
                    employee.week_type,
                    ss_in_date.strftime('%d%m%Y') if in_date > min_in_date else min_in_date.strftime('%d%m%Y'),
                    str("%.2f" % (first_wage if first_wage > 0 else contract.sdi)).replace('.','').zfill(7),
                    employee.expense_id.name[:17].ljust(17),
                    ' ' * 10,
                    ' ' * 8,
                    ' ',
                    '0' * 8
                )


            self.execute("mkdir -p %s" % out_path)

            f = open(filename, 'w')
            f.write(txt_content)
            f.close()

            # ENCODE FILE
            self.execute('iconv -f utf-8 -t iso-8859-1 "%s" > "%s"' % (filename, file_encoded))

            return {
                'type' : 'ir.actions.act_url',
                'url': '/web/download/raw_file/?path=%s&_type=%s&filename=%s' % (urllib.quote_plus(file_encoded), urllib.quote_plus('text/plain; charset=iso-8859-1'), 'EMP_%s.txt' % self.employer_id.name),
                'target': 'new',
            }

        if self.file_type == '04':

            out_path = '/tmp/odoo_txt/%s' % uuid.uuid4()
            filename = '%s/employee_data.txt' % out_path
            file_encoded = '%s/employee_data_encoded.txt' % out_path
            txt_content = ''

            employees = self.env['hr.employee'].search([
                ('employer_registration', '=', self.employer_id.id),
                '|',
                ('active', '=',True),
                ('active', '=', False)
            ])

            emp_old_ids = ','.join(str(employee.old_id) for employee in employees)

            remote_absences = eval(self.execute('%s/incidents_query.php A %s %s' % (self._BASE_COMMAND, self.company_id.old_db, emp_old_ids)))
            remote_incidents = eval(self.execute('%s/incidents_query.php I %s %s' % (self._BASE_COMMAND, self.company_id.old_db, emp_old_ids)))

            for employee in employees:

                abs_key = str(employee.old_id)

                if abs_key in remote_absences.keys():

                    for absence in remote_absences[abs_key]:

                        move = self.env['hr.absence'].search([('old_id', '=', int(absence[2]))], limit=1)

                        if move.id:
                            continue

                        self.env['hr.absence'].create({
                            'employee_id': employee.id,
                            'old_id': absence[2],
                            'from_date': absence[0],
                            'to_date': absence[1]
                        })

                if abs_key in remote_incidents.keys():

                    for incident in remote_incidents[abs_key]:

                        move = self.env['hr.ss.move'].search([('folio','=', incident[0])], limit=1)

                        if move.id:
                            continue

                        self.env['hr.ss.move'].create({
                            'employee_id': employee.id,
                            'folio': incident[0],
                            'from_date': incident[1],
                            'to_date': incident[2],
                            'inhability_type': str(incident[3])
                        })

            employee_ids = [employee.id for employee in employees]

            absences = self.env['hr.absence'].search([
                ('employee_id', 'in', employee_ids),
                ('to_date','>=', self.from_date),
                ('from_date','<=', self.to_date)
            ])

            for absence in absences:

                from_date = datetime.strptime(absence.from_date, DEFAULT_SERVER_DATE_FORMAT)
                to_date = datetime.strptime(absence.to_date, DEFAULT_SERVER_DATE_FORMAT)

                txt_content += '%s%s%s%s%s%s%s\r\n' % (
                    absence.employee_id.employer_registration.name,
                    absence.employee_id.ssn,
                    '11',
                    from_date.strftime('%d%m%Y'),
                    ' ' * 8,
                    str((to_date - from_date).days + 1).zfill(2),
                    '0' * 7
                )

            incidents = self.env['hr.ss.move'].search([
                ('employee_id', 'in', [employee.id for employee in employees]),
                ('to_date','>=', self.from_date),
                ('from_date','<=', self.to_date)
            ])

            for incident in incidents:

                from_date = datetime.strptime(incident.from_date, DEFAULT_SERVER_DATE_FORMAT)
                to_date = datetime.strptime(incident.to_date, DEFAULT_SERVER_DATE_FORMAT)

                txt_content += '%s%s%s%s%s%s%s\r\n' % (
                    incident.employee_id.employer_registration.name,
                    incident.employee_id.ssn,
                    '12',
                    from_date.strftime('%d%m%Y'),
                    incident.folio,
                    str((to_date - from_date).days + 1).zfill(2),
                    '0' * 7
                )

            contracts = self.env['hr.contract'].search([
                ('employee_id', 'in', [employee.id for employee in employees]),
                ('for_paysheet', '=', True),
                '|',
                ('active', '=',True),
                ('active', '=', False)
            ])

            wage_changes = self.env['hr.salary.change'].search([
                ('contract_id', 'in', [contract.id for contract in contracts]),
                ('move_date','>=', self.from_date),
                ('move_date','<=', self.to_date)
            ])

            for wage_change in wage_changes:

                if wage_change.old_sdi == wage_change.new_sdi:
                    continue

                employee = wage_change.contract_id.employee_id
                move_date = datetime.strptime(wage_change.move_date, DEFAULT_SERVER_DATE_FORMAT)

                txt_content += '%s%s%s%s%s%s%s\r\n' % (
                    self.employer_id.name,
                    employee.ssn,
                    '07',
                    move_date.strftime('%d%m%Y'),
                    ' ' * 8,
                    '0' * 2,
                    ("%.2f" % wage_change.new_sdi).replace('.','').zfill(7)
                )

            new_employees = self.env['hr.employee'].search([
                ('employer_registration', '=', self.employer_id.id),
                ('ss_in_date','>=', self.from_date),
                ('ss_in_date','<=', self.to_date),
                '|', ('active', '=',True), ('active', '=', False)
            ])

            for new_employee in new_employees:

                contract = self.env['hr.contract'].search([
                    ('employee_id', '=', new_employee.id),
                    ('company_id', '=', new_employee.company_id.id),
                    ('for_paysheet', '=', True),
                    '|', ('active', '=',True), ('active', '=', False)
                ], limit=1)

                if not contract:
                    _logger.debug("SIN CONTRATO: %s", new_employee.id)
                    continue

                ss_in_date = datetime.strptime(new_employee.ss_in_date, DEFAULT_SERVER_DATE_FORMAT)

                first_sc = self.env['hr.salary.change'].search([
                    ('contract_id', '=', contract.id),
                    ('move_date','>=', self.from_date),
                    ('move_date','<=', self.to_date)
                ], order = 'id DESC', limit=1)

                report_sdi = contract.sdi

                if first_sc:
                    report_sdi = first_sc.old_sdi if first_sc.old_sdi > 0 else contract.sdi

                txt_content += '%s%s%s%s%s%s%s\r\n' % (
                    new_employee.employer_registration.name,
                    new_employee.ssn,
                    '08',
                    ss_in_date.strftime('%d%m%Y'),
                    ' ' * 8,
                    '0' * 2,
                    ("%.2f" % report_sdi).replace('.','').zfill(7)
                )

            work_leaves = self.env['hr.employee'].search([
                ('employer_registration', '=', self.employer_id.id),
                ('ss_out_date','>=', self.from_date),
                ('ss_out_date','<=', self.to_date),
                '|', ('active', '=',True), ('active', '=', False)
            ])

            for work_leave in work_leaves:

                ss_out_date = datetime.strptime(work_leave.ss_out_date, DEFAULT_SERVER_DATE_FORMAT)

                txt_content += '%s%s%s%s%s%s%s\r\n' % (
                    work_leave.employer_registration.name,
                    work_leave.ssn,
                    '02',
                    ss_out_date.strftime('%d%m%Y'),
                    ' ' * 8,
                    '0' * 2,
                    '0' * 7
                )

            if len(txt_content.strip()) == 0:
                raise UserError('No se encontraron registros')

            self.execute("mkdir -p %s" % out_path)

            f = open(filename, 'w')
            f.write(txt_content)
            f.close()

            # ENCODE FILE
            self.execute('iconv -f utf-8 -t iso-8859-1 "%s" > "%s"' % (filename, file_encoded))

            return {
                'type' : 'ir.actions.act_url',
                'url': '/web/download/raw_file/?path=%s&_type=%s&filename=%s' % (urllib.quote_plus(file_encoded), urllib.quote_plus('text/plain; charset=iso-8859-1'), 'MOV_%s.txt' % self.employer_id.name),
                'target': 'new',
            }

        if self.file_type == '05':

            from_date = datetime.strptime(self.from_date, DEFAULT_SERVER_DATE_FORMAT)
            to_date = datetime.strptime(self.to_date, DEFAULT_SERVER_DATE_FORMAT)
            out_path = '/tmp/odoo_txt/%s' % uuid.uuid4()
            filename = '%s/incapacidades.txt' % out_path
            file_encoded = '%s/incapacidades_encoded.txt' % out_path
            txt_content = ''
            employees = self.env['hr.employee'].search([('employer_registration', '=', self.employer_id.id)], order="old_id")
            emp_old_ids = ','.join(str(employee.old_id) for employee in employees)
            remote_incidents = eval(self.execute('%s/incidents_query.php I %s %s' % (self._BASE_COMMAND, self.company_id.old_db, emp_old_ids)))

            for employee in employees:

                abs_key = str(employee.old_id)

                if abs_key in remote_incidents.keys():

                    for incident in remote_incidents[abs_key]:

                        move = self.env['hr.ss.move'].search([('folio','=', incident[0])], limit=1)

                        if move.id:
                            continue

                        self.env['hr.ss.move'].create({
                            'employee_id': employee.id,
                            'folio': incident[0],
                            'from_date': incident[1],
                            'to_date': incident[2],
                            'inhability_type': str(incident[3])
                        })

            incidents = self.env['hr.ss.move'].search([
                ('employee_id', 'in', [employee.id for employee in employees]),
                ('from_date','>=', self.from_date),
                ('from_date','<=', self.to_date)
            ])

            if len(incidents) == 0:
                raise UserError('No se encontraron registros')

            for incident in incidents:

                from_date = datetime.strptime(incident.from_date, DEFAULT_SERVER_DATE_FORMAT)
                to_date = datetime.strptime(incident.to_date, DEFAULT_SERVER_DATE_FORMAT)

                if incident.inhability_type == '3':
                    incident_control = incident.maternity_control or '0'

                if incident.inhability_type == '2':
                    incident_control = incident.disease_control or '0'

                if incident.inhability_type == '1':
                    incident_control = incident.implication_control or incident.single_control or '0'

                txt_content += '%s%s%s%s%s%s%s%s%s%s%s%s\r\n' % (
                    incident.employee_id.employer_registration.name,
                    incident.employee_id.ssn,
                    '0',
                    from_date.strftime('%d%m%Y'),
                    incident.folio,
                    str((to_date - from_date).days + 1).zfill(3),
                    str(incident.inhability_percent).zfill(3),
                    incident.inhability_type,
                    incident.inhability_risk or '0',
                    incident.implication or '0',
                    incident_control,
                    to_date.strftime('%d%m%Y')
                )

            self.execute("mkdir -p %s" % out_path)

            f = open(filename, 'w')
            f.write(txt_content)
            f.close()

            # ENCODE FILE
            self.execute('iconv -f utf-8 -t iso-8859-1 "%s" > "%s"' % (filename, file_encoded))

            return {
                'type' : 'ir.actions.act_url',
                'url': '/web/download/raw_file/?path=%s&_type=%s&filename=%s' % (urllib.quote_plus(file_encoded), urllib.quote_plus('text/plain; charset=iso-8859-1'), 'INC_%s.txt' % self.employer_id.name),
                'target': 'new',
            }

        if self.file_type == '06':

            from_date = datetime.strptime(self.from_date, DEFAULT_SERVER_DATE_FORMAT)
            to_date = datetime.strptime(self.to_date, DEFAULT_SERVER_DATE_FORMAT)
            out_path = '/tmp/odoo_txt/%s' % uuid.uuid4()
            filename = '%s/idse.txt' % out_path
            file_encoded = '%s/idse_encoded.txt' % out_path
            txt_content = ''

            employees = self.env['hr.employee'].search([
                ('employer_registration', '=', self.employer_id.id)
            ])

            contracts = self.env['hr.contract'].search([
                ('employee_id', 'in', [employee.id for employee in employees]),
                ('for_paysheet', '=', True)
            ])

            salary_changes = self.env['hr.salary.change'].search([
                ('contract_id', 'in', [contract.id for contract in contracts]),
                ('move_date','>=', self.from_date),
                ('move_date','<=', self.to_date)
            ])

            if not len(salary_changes):
                raise UserError('No se encontraron registros')

            for salary_change in salary_changes:

                if salary_change.old_sdi == salary_change.new_sdi:
                    continue

                if not employee.sua_name:
                    raise UserError('Nombre SUA no encontrado: %s - %s', employee.name_related, employee.id)

                employee = salary_change.contract_id.employee_id
                emp_name = ''.join( word.strip()[:27].ljust(27) for word in employee.sua_name.split('$') )
                movement_date = datetime.strptime(salary_change.move_date, DEFAULT_SERVER_DATE_FORMAT)

                txt_content += '%s%s%s%s%s%s%s%s%s%s%s%s%s%s\r\n' % (
                    self.employer_id.name,
                    employee.ssn,
                    emp_name,
                    ("%.2f" % salary_change.new_sdi).replace('.','').zfill(6),
                    ' ' * 6,
                    employee.worker_type,
                    employee.wage_type,
                    employee.week_type,
                    movement_date.strftime('%d%m%Y'),
                    ' ' * 5,
                    '07',
                    self.employer_id.guide or ' ' * 7,
                    str(employee.old_id).rjust(10),
                    '9'.rjust(20)
                )

            self.execute("mkdir -p %s" % out_path)

            f = open(filename, 'w')
            f.write(txt_content)
            f.close()

            # ENCODE FILE
            self.execute('iconv -f utf-8 -t iso-8859-1 "%s" > "%s"' % (filename, file_encoded))

            return {
                'type' : 'ir.actions.act_url',
                'url': '/web/download/raw_file/?path=%s&_type=%s&filename=%s' % (urllib.quote_plus(file_encoded), urllib.quote_plus('text/plain; charset=iso-8859-1'), 'IDSE_%s.txt' % self.employer_id.name),
                'target': 'new',
            }

        if self.file_type == '07':

            from_date = datetime.strptime(self.from_date, DEFAULT_SERVER_DATE_FORMAT)
            to_date = datetime.strptime(self.to_date, DEFAULT_SERVER_DATE_FORMAT)
            out_path = '/tmp/odoo_txt/%s' % uuid.uuid4()
            filename = '%s/movcr.txt' % out_path
            file_encoded = '%s/movcr_encoded.txt' % out_path
            txt_content = ''

            employees = self.env['hr.employee'].search([
                ('employer_registration', '=', self.employer_id.id),
                ('mov_date','>=', self.from_date),
                ('mov_date','<=', self.to_date),
                '|', ('active', '=',True), ('active', '=', False)
            ])

            if not len(employees):
                raise UserError('No se encontraron registros')

            for employee in employees:

                movement_date = datetime.strptime(employee.mov_date, DEFAULT_SERVER_DATE_FORMAT)

                if employee.discount_type == '1':
                    discount_value = ('00%.2f00' % employee.sdi_percent).replace('.','')

                if employee.discount_type == '2':
                    discount_value = ('%.2f0' % employee.cf_fixed_amount).replace('.','').zfill(8)

                if employee.discount_type == '3':
                    discount_value = ('%.4f' % employee.vs_number).replace('.','').zfill(8)

                txt_content += '%s%s%s%s%s%s%s%s\r\n' % (
                    self.employer_id.name,
                    employee.ssn,
                    employee.credit_number,
                    employee.mov_type,
                    movement_date.strftime('%d%m%Y'),
                    employee.discount_type,
                    discount_value,
                    'S' if employee.apply_table else 'N'
                )

            self.execute("mkdir -p %s" % out_path)

            f = open(filename, 'w')
            f.write(txt_content)
            f.close()

            # ENCODE FILE
            self.execute('iconv -f utf-8 -t iso-8859-1 "%s" > "%s"' % (filename, file_encoded))

            return {
                'type' : 'ir.actions.act_url',
                'url': '/web/download/raw_file/?path=%s&_type=%s&filename=%s' % (urllib.quote_plus(file_encoded), urllib.quote_plus('text/plain; charset=iso-8859-1'), 'CRED_%s.txt' % self.employer_id.name),
                'target': 'new',
            }

        if self.file_type == '08':

            from_date = datetime.strptime(self.from_date, DEFAULT_SERVER_DATE_FORMAT)
            to_date = datetime.strptime(self.to_date, DEFAULT_SERVER_DATE_FORMAT)
            out_path = '/tmp/odoo_txt/%s' % uuid.uuid4()
            filename = '%s/datos_afil.sql' % out_path
            txt_content = ''

            new_employees = self.env['hr.employee'].search([
                ('employer_registration', '=', self.employer_id.id),
                ('ss_in_date','>=', self.from_date),
                ('ss_in_date','<=', self.to_date),
                '|', ('active', '=',True), ('active', '=', False)
            ])

            if not len(new_employees):
                raise UserError('No se encontraron registros')

            gender = {
                'H': 'M',
                'M': 'F'
            }

            for employee in new_employees:

                txt_content += "INSERT INTO Afiliacion (REG_PATR, NUM_AFIL, CPP_TRAB, FEC_NAC, LUG_NAC, ENT_TRAB, UMF_TRAB, OCUPA, SEXO, TIP_SAL, JOR_HOR, CVE_MUN) "
                txt_content += "VALUES ('%s','%s', %s, %s, %s, %s, %s, %s, %s, %s, NULL,'%s');\r\n" % (
                    self.employer_id.name,
                    employee.ssn,
                    "'%s'" % employee.zip_code if employee.zip_code else 'NULL',
                    "'%s'" % datetime.strptime(employee.birth_date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y') if employee.birth_date else 'NULL',
                    "'%s'" % employee.sua_state_id.name if employee.sua_state_id else 'NULL',
                    employee.sua_state_id.code if employee.sua_state_id else 'NULL',
                    "'%s'" % str(int(employee.umf)).zfill(3) if employee.umf else 'NULL',
                    "'%s'" % employee.job_id.name.upper()[:15] if employee.job_id else 'NULL',
                    "'%s'" % gender[employee.emp_gender] if employee.emp_gender else 'NULL',
                    int(employee.wage_type) if employee.wage_type else 'NULL',
                    self.employer_id.name[:3]
                )

            self.execute("mkdir -p %s" % out_path)

            f = open(filename, 'w')
            f.write(txt_content)
            f.close()

            return {
                'type' : 'ir.actions.act_url',
                'url': '/web/download/raw_file/?path=%s&_type=%s&filename=%s' % (urllib.quote_plus(filename), urllib.quote_plus('text/plain; charset=utf-8'), 'datos_afil_%s.sql' % self.employer_id.name),
                'target': 'new',
            }

    def locale_format(self, _date, _format, _capital = False, _position = 3, _locale = 'es_MX.UTF-8'):

        # Convenrt date to locale format
        locale.setlocale(locale.LC_TIME, _locale)

        res = _date.strftime(_format)

        if(_capital):
            s = list(res)
            s[_position] = s[_position].upper()
            res = "".join(s)

        return res

    def execute(self, _command):
        try:
            return subprocess.check_output(_command, shell=True, stderr=subprocess.STDOUT)
        except Exception, e:
            _logger.error('EXECUTE ERROR: %s', e)

    @api.onchange('file_type')
    def change_file_type(self):

        current_date = datetime.today()

        if self.file_type in ('01','02','03','04','05','07','08'):

            last_month = current_date.month - 1
            last_year = current_date.year

            if current_date.month == 1:
                last_month = 12
                last_year = current_date.year - 1

            last_day = calendar.monthrange(last_year, last_month)[1]
            self.from_date = current_date.replace(day=1, month=last_month, year=last_year)
            self.to_date = current_date.replace(day=last_day, month=last_month, year=last_year)
            return

        BYMONTH_TABLE = [
            (1,2),
            (3,4),
            (5,6),
            (7,8),
            (9,10),
            (11,12)
        ]

        last_period = -1
        last_year = current_date.year

        for num, period in enumerate(BYMONTH_TABLE):

            if period[0] == current_date.month or period[1] == current_date.month:

                if num == 0:
                    last_year -= 1
                    last_period = 5
                    continue

                last_period = num - 1

        last_day = calendar.monthrange(last_year, BYMONTH_TABLE[last_period][1])[1]
        self.from_date = current_date.replace(day=1, month=BYMONTH_TABLE[last_period][0], year=last_year)
        self.to_date = current_date.replace(day=last_day, month=BYMONTH_TABLE[last_period][1], year=last_year)

    @api.onchange('company_id')
    def change_company_id(self):

        if self.employer_id:
            self.employer_id = False