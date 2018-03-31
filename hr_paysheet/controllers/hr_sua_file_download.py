# -*- coding: utf-8 -*-

from datetime import datetime
import base64
import locale
import logging
import sys

from openerp import http
from openerp.addons.web.controllers.main import serialize_exception,content_disposition
from openerp.http import request
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)

class XMlPrinter(http.Controller):

    @http.route('/web/binary/sua_file_download', type='http', auth="user")
    @serialize_exception
    def sua_file_download(self, id, model, **kw):
        """ Download sua txt file.
        @returns: :class:`werkzeug.wrappers.Response`
        """

        wizard = http.request.env[model].search([('id','=',id)], limit=1)

        filename = wizard.name

        return request.make_response(
            wizard.file_content,
            [
                ('Content-Type', 'text/plain'),
                ('Content-Disposition', content_disposition(filename))
            ]
        )

    @http.route('/web/reports/hr_wage_report', type='http', auth="user")
    @serialize_exception
    def hr_wage_report(self, **kw):
        """ Download xls report file.
        @returns: :class:`werkzeug.wrappers.Response`
        """

        # SET DEAFULT ENCODING AS UTF-8
        reload(sys)
        sys.setdefaultencoding('utf-8')

        # SET LOCALE
        locale.setlocale(locale.LC_ALL, 'es_MX.UTF-8')

        # GET BASE VALUES
        http.request.env.cr.execute("""
            SELECT
                he.id AS employee_id,
                rc.name AS cname,
                he.old_id,
                he.name_related,
                he.in_date,
                find_department(he.department_id) AS department_name,
                ar.name  AS area,
                job.name AS job_name,
                COALESCE(pr.name, '-') AS emp_profesion,
                COALESCE(hal.name, '-') AS academic_level,
                COALESCE(hal.antique_bonus, FALSE) AS academic_bonus,
                EXTRACT(year FROM age(he.in_date)) || ' Año(s) ' ||
                EXTRACT(month FROM age(he.in_date)) || ' Mes(es) ' ||
                EXTRACT(day FROM age(he.in_date)) || ' Día(s)' AS antique_time,
                hc.wage AS wage,
                hc.sdi AS sbc,
                CASE
                    WHEN he.has_medical_insurance THEN he.medical_insurance
                    ELSE 0
                END AS insurance, (
                    SELECT pb.amount
                    FROM hr_paysheet_benefit pb
                    INNER JOIN hr_paysheet_concept pbc ON pb.concept_id = pbc.id
                    WHERE pb.contract_id = hc.id AND pbc.code = 36
                ) AS holidays, (
                    SELECT pb.amount
                    FROM hr_paysheet_benefit pb
                    INNER JOIN hr_paysheet_concept pbc ON pb.concept_id = pbc.id
                    WHERE pb.contract_id = hc.id AND pbc.code = 24
                ) AS xmas_bonus, COALESCE((
                    SELECT pb.amount
                    FROM hr_paysheet_benefit pb
                    INNER JOIN hr_paysheet_concept pbc ON pb.concept_id = pbc.id
                    WHERE pb.contract_id = hc.id AND pbc.code = 14
                ),0) AS ptu_days, COALESCE((
                    SELECT pb.amount
                    FROM hr_paysheet_benefit pb
                    INNER JOIN hr_paysheet_concept pbc ON pb.concept_id = pbc.id
                    WHERE pb.contract_id = hc.id AND pbc.code = 17
                ),0) AS savings_fund,
                EXTRACT(year FROM age(he.in_date)) AS ant_years,
                COALESCE((
                    SELECT pb.amount
                    FROM hr_paysheet_benefit pb
                    INNER JOIN hr_paysheet_concept pbc ON pb.concept_id = pbc.id
                    WHERE pb.contract_id = hc.id AND pbc.code = 15
                ),0) AS pantry, COALESCE((
                    SELECT pb.amount
                    FROM hr_paysheet_benefit pb
                    INNER JOIN hr_paysheet_concept pbc ON pb.concept_id = pbc.id
                    WHERE pb.contract_id = hc.id AND pbc.code = 38
                ), 0) AS work_bonus,
                he.vehicle_id

            FROM hr_employee he

                INNER JOIN resource_resource rr ON he.resource_id = rr.id
                INNER JOIN res_company rc ON rr.company_id = rc.id
                INNER JOIN hr_department ar ON he.department_id = ar.id
                LEFT  JOIN hr_profession pr ON he.profession_id = pr.id
                LEFT  JOIN hr_academic_level hal ON he.academic_level_id = hal.id
                INNER JOIN hr_job job ON he.job_id = job.id
                INNER JOIN hr_contract hc ON hc.employee_id = he.id AND hc.for_paysheet = TRUE AND hc.active = TRUE

            WHERE rr.active = TRUE AND rc.id IN (%s)

            ORDER BY old_id, department_name, area, job_name

        """ % kw['ids'])

        # FORMAT VALUES

        res_str = '<table border="1" cellpadding="0" width="7000px">'

        res_str += '<tr bgcolor="B0CBF0">'
        res_str += '<td>Empresa</td><td>Clv. Emp.</td><td>Nombre</td><td>Antigüedad</td><td>Departamento</td><td>Área</td><td>Puesto</td><td>Estudios</td>'
        res_str += '<td>Años Antigüedad</td><td>Nivel Académico</td><td>SBD</td><td>SBC</td><td>Días Vacaciones</td><td>Días Aguinaldo</td><td>Días PTU</td>'
        res_str += '<td>% FA</td><td>% Bono Antigüedad</td><td>Despensa diaria</td><td>Despensa</td><td>Despensa anual</td><td>Premio Asistencia Diario</td><td>Premio Asistencia Mensual</td><td>Premio Asistencia Anual</td><td>Aguinaldo diario</td><td>Aguinaldo mensual</td><td>Aguinaldo</td><td>Prima Vacacional Diaria</td><td>Prima Vacacional Mensual</td><td>Prima Vacacional</td><td>PTU diario</td><td>PTU mensual</td><td>PTU</td>'
        res_str += '<td>FA diario</td><td>FA mensual</td><td>FA anual</td><td>Bono Antigüedad diario</td><td>Bono Antigüedad</td><td>Bono Antigüedad anual</td><td>Bono Anual diario</td><td>Bono Anual mensual</td><td>Bono Anual</td><td>SGM diario</td><td>SGM mensual</td><td>SGM</td><td>SDI</td><td>Salario mensual</td><td>Salario anual</td><td>Vehículo</td>'
        res_str += '</tr>'

        for row in http.request.env.cr.fetchall():

            # FORMAT ANTIQUE DATE
            ant_date = datetime.strptime(row[4], DEFAULT_SERVER_DATE_FORMAT)
            ant_date_str = ant_date.strftime('%d/%b/%Y')
            s = list(ant_date_str)
            s[3] = s[3].upper()
            ant_date_str = "".join(s)

            ant_bonus_row = http.request.env['hr.rank.table'].find_value('ANTIQ_BONUS', row[19])
            year_bonus_row = http.request.env['hr.rank.table'].find_value('YEAR_BONUS_P' if row[10] else 'YEAR_BONUS', row[19])

            results_map = {
                'company': row[1],
                'emp_key': row[2],
                'emp_name': row[3],
                'emp_ant': ant_date_str,
                'emp_dep': row[5],
                'emp_ar': row[6],
                'emp_job': row[7],
                'profession': row[8],
                'ac_level': row[9],
                'ant_years': row[11],
                'sbd': row[12],
                'sbc': row[13],
                'holidays': int(row[15]),
                'xmas_bonus': int(row[16]),
                'ptu_days': int(row[17]),
                'savings_fund': row[18],
                'ant_bonus': int(ant_bonus_row.fixed_amount) if ant_bonus_row else 0,
                'pantry': row[20],
                'work_bonus': row[21],
                'year_bonus': int(year_bonus_row.fixed_amount) if year_bonus_row else 0,
                'medical_insurance': row[14],
                'vehicle': http.request.env['fleet.vehicle'].browse(row[22]) if row[22] else False
            }

            row_str  = '<tr>'
            row_str += '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>'
            row_str += '<td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td>'
            row_str += '<td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td>'
            row_str += '<td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td>'
            row_str += '<td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td>'
            row_str += '<td>%s</td></tr>'

            # CALC XMAS BONUS
            xbonus = (results_map['sbd'] + results_map['pantry'] / 30.4166) * results_map['xmas_bonus']
            holidays_bonus = 0.25 * results_map['holidays'] * results_map['sbd']
            ptu = results_map['ptu_days'] * (results_map['sbd'] + results_map['pantry'] / 30.4166)
            sf_amount = (results_map['sbd'] * 7 * (results_map['savings_fund'] / 100.0)) * 2 * 52
            ant_bonus = results_map['sbd'] * (results_map['ant_bonus'] / 100.0) * 30.4166
            year_bonus = results_map['year_bonus'] * (results_map['sbd'] + results_map['pantry'] / 30.4166)
            daily_benefits = results_map['pantry'] / 30.4166
            daily_benefits += results_map['work_bonus'] / 30.4166
            daily_benefits += xbonus / 365.0
            daily_benefits += holidays_bonus / 365.0
            daily_benefits += ptu / 365.0
            daily_benefits += sf_amount / 365.0
            daily_benefits += ant_bonus / 30.4166
            daily_benefits += year_bonus / 365.0
            year_benefits = results_map['pantry'] * 12
            year_benefits += results_map['work_bonus'] * 12
            year_benefits += xbonus
            year_benefits += holidays_bonus
            year_benefits += ptu
            year_benefits += sf_amount
            year_benefits += ant_bonus * 12
            year_benefits += year_bonus
            year_benefits += results_map['medical_insurance']
            sdi = results_map['sbd'] + daily_benefits + (results_map['medical_insurance'] / 365.0)
            month_wage = (results_map['sbd'] + daily_benefits) * 30.4166
            year_wage = results_map['sbd'] * 365 + year_benefits


            res_str += row_str % (
                results_map['company'],
                results_map['emp_key'],
                results_map['emp_name'],
                results_map['emp_ant'],
                results_map['emp_dep'],
                results_map['emp_ar'],
                results_map['emp_job'],
                results_map['profession'],
                results_map['ant_years'],
                results_map['ac_level'],
                "{:,.2f}".format(results_map['sbd']),
                "{:,.2f}".format(results_map['sbc']),
                results_map['holidays'],
                results_map['xmas_bonus'],
                results_map['ptu_days'],
                "%s %%" % int(results_map['savings_fund']),
                "%s %%" % results_map['ant_bonus'],
                "{:,.2f}".format(results_map['pantry'] / 30.4166),
                "{:,.2f}".format(results_map['pantry']),
                "{:,.2f}".format(results_map['pantry'] * 12),
                "{:,.2f}".format(results_map['work_bonus'] / 30.4166),
                "{:,.2f}".format(results_map['work_bonus']),
                "{:,.2f}".format(results_map['work_bonus'] * 12),
                "{:,.2f}".format(xbonus / 365.0),
                "{:,.2f}".format(xbonus / 12.0),
                "{:,.2f}".format(xbonus),
                "{:,.2f}".format(holidays_bonus / 365.0),
                "{:,.2f}".format(holidays_bonus / 12.0),
                "{:,.2f}".format(holidays_bonus),
                "{:,.2f}".format(ptu / 365.0),
                "{:,.2f}".format(ptu / 12.0),
                "{:,.2f}".format(ptu),
                "{:,.2f}".format(sf_amount / 365.0),
                "{:,.2f}".format(sf_amount / 12.0),
                "{:,.2f}".format(sf_amount),
                "{:,.2f}".format(ant_bonus / 30.4166),
                "{:,.2f}".format(ant_bonus),
                "{:,.2f}".format(ant_bonus * 12),
                "{:,.2f}".format(year_bonus / 365.0),
                "{:,.2f}".format(year_bonus / 12.0),
                "{:,.2f}".format(year_bonus),
                "{:,.2f}".format(results_map['medical_insurance'] / 365.0),
                "{:,.2f}".format(results_map['medical_insurance'] / 12.0),
                "{:,.2f}".format(results_map['medical_insurance']),
                "{:,.2f}".format(sdi),
                "{:,.2f}".format(month_wage),
                "{:,.2f}".format(year_wage),
                results_map['vehicle'].name if results_map['vehicle'] else '-'
            )



        res_str += '</table>'


        # CLEAN RESPONSE
        replacements = {
            'á': '&aacute;',
            'Á': '&Aacute;',
            'é': '&eacute;',
            'í': '&iacute;',
            'ó': '&oacute;',
            'ú': '&uacute;',
            'Ñ': '&Ntilde;',
            'ñ': '&ntilde;',
            'ü': '&uuml;',
            'Ü': '&Uuml;',
            ' ': ','
        }

        for key, value in replacements.iteritems():
            res_str = res_str.replace(key, value)

        if kw['export_type'] == 'X':

            return request.make_response(
                res_str,
                [
                    ('Content-Type', 'application/ms-excel; charset=UTF-8'),
                    ('Content-Disposition', content_disposition('sueldos.xls'))
                ]
            )

        return res_str

    @http.route('/web/reports/hr_ptu_report', type='http', auth="user")
    @serialize_exception
    def hr_ptu_report(self, **kw):
        """ Download xls report file.
        @returns: :class:`werkzeug.wrappers.Response`
        """


        # SET DEAFULT ENCODING AS UTF-8
        reload(sys)
        sys.setdefaultencoding('utf-8')

        # SET LOCALE
        locale.setlocale(locale.LC_ALL, 'es_MX.UTF-8')

        if str(kw['type']) == 'PR':

            res_str = '<table border="1" cellpadding="0" width="1600px">'

            res_str += '<tr bgcolor="B0CBF0">'
            res_str += '<td>Empresa</td><td>Clave</td><td>Nombre</td><td>Fecha baja</td><td>Cuenta contable</td><td>Segmento</td><td>Días efectivos trabajados</td>'
            res_str += '<td>Salario base diario</td><td>Días de P.T.U.</td><td>Despensa diaria</td><td>PTU Pagado</td>'
            res_str += '<td>Neto proyectado</td><td>PTU a entregar</td>'
            res_str += '</tr>'

            for line in http.request.env['hr.ptu.line'].search([('wizard_id', '=', int(kw['wizard_id']))]):

                http.request.env.cr.execute("""
                    SELECT COALESCE(sc.base_account, 0)
                    FROM hr_employee he
                    INNER JOIN resource_resource rr ON he.resource_id = rr.id
                    INNER JOIN hr_account_expense ae ON he.expense_id = ae.id
                    INNER JOIN hr_segment_config sc ON sc.segment_id = ae.id
                    WHERE he.id = %s AND (sc.company_id = %s OR sc.company_id IS NULL)
                """ % (line.employee_id.id, line.employee_id.company_id.id))

                base_account = http.request.env.cr.fetchone()[0]

                row_str  = '<tr>'
                row_str += '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td align="right">%s</td>'
                row_str += '<td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td>'
                row_str += '<td align="right">%s</td><td align="right">%s</td>'
                row_str += '</tr>'

                res_str += row_str % (
                    line.employee_id.company_id.short_name,
                    line.employee_id.old_id,
                    line.employee_id.name,
                    line.employee_id.out_date or '',
                    base_account or '',
                    line.employee_id.segment_id.code if line.employee_id.segment_id.id else '',
                    "{:,.6f}".format(line.worked_days),
                    "{:,.2f}".format(line.wage),
                    line.ptu_days,
                    line.daily_pantry,
                    "{:,.2f}".format(line.ptu_amount),
                    "{:,.2f}".format(line.amount),
                    "{:,.2f}".format(max(0, line.amount - line.ptu_amount))
                )

            res_str += '</table>'

        if str(kw['type']) == 'CA':

            if str(kw['export_type']) in ('SHEE','PREV'):

                res_str = '<table border="1" cellpadding="0" width="2000px">'

                res_str += '<tr bgcolor="B0CBF0">'
                res_str += '<td>Empresa</td><td>Clave</td><td>Nombre</td><td>Fecha baja</td><td>Antigüedad</td>'
                res_str += '<td>Sindicalizado</td><td>Sueldo base</td><td>Sueldo tope</td><td>Topado</td>'
                res_str += '<td>Sueldo limite</td><td>Días trabajados</td><td>Ingreso anual por sueldo base</td>'
                res_str += '<td>PTU por días trabajados</td><td>PTU por sueldo base</td><td>PTU total</td>'
                res_str += '<td>Sueldo mensual</td><td>PTU a entregar</td>'
                res_str += '</tr>'

                for line in http.request.env['hr.ptu.line'].search([('wizard_id', '=', int(kw['wizard_id']))]):

                    row_str  = '<tr>'
                    row_str += '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td align="center">%s</td><td align="right">%s</td>'
                    row_str += '<td align="center">%s</td><td align="center">%s</td><td align="right">%s</td><td align="right">%s</td>'
                    row_str += '<td align="right">%s</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td>'
                    row_str += '<td align="right">%s</td><td align="right">%s</td>'
                    row_str += '</tr>'

                    total_ptu = line.wd_ptu + line.wage_ptu

                    res_str += row_str % (
                        line.employee_id.company_id.short_name,
                        line.employee_id.old_id,
                        line.employee_id.name,
                        line.employee_id.out_date or '',
                        line.employee_id.in_date,
                        'SI' if line.employee_id.labor_union else '',
                        "{:,.2f}".format(line.last_wage),
                        'SI' if line.has_max_wage else '',
                        '< %.2f' % line.base_wage if line.base_wage > line.last_wage else '',
                        "{:,.2f}".format(line.wage_limit),
                        "{:,.6f}".format(line.worked_days),
                        "{:,.2f}".format(line.wage),
                        "{:,.2f}".format(line.wd_ptu),
                        "{:,.2f}".format(line.wage_ptu),
                        "{:,.2f}".format(total_ptu),
                        "{:,.2f}".format(line.month_wage),
                        "{:,.2f}".format(min(line.wage_limit, total_ptu) if line.company_line_id.company_id.has_ptu else min(line.month_wage, total_ptu)),
                    )

                res_str += '</table>'

            elif str(kw['export_type']) in ('EXPO'):

                res_str = '<table>'

                for c_line in http.request.env['hr.ptu.company.line'].search([('wizard_id', '=', int(kw['wizard_id']))]):

                    for line in http.request.env['hr.ptu.line'].search([('company_line_id', '=', c_line.id)]):

                        row_str  = '<tr>'
                        row_str += '<td>%s</td><td>%s</td><td>%s</td><td>%s</td>'
                        row_str += '</tr>'

                        res_str += row_str % (
                            line.employee_id.company_id.short_name,
                            line.employee_id.old_id,
                            '14',
                            round(line.wd_ptu + line.wage_ptu),
                        )

                    res_str += '<tr><td colspan="4"></td></tr>'
                    res_str += '<tr><td colspan="4"></td></tr>'

                res_str += '</table>'

            else:

                res_str = ''


        # CLEAN RESPONSE

        replacements = {
            'á': '&aacute;',
            'Á': '&Aacute;',
            'é': '&eacute;',
            'í': '&iacute;',
            'ó': '&oacute;',
            'ú': '&uacute;',
            'Ñ': '&Ntilde;',
            'ñ': '&ntilde;',
            'ü': '&uuml;',
            'Ü': '&Uuml;',
            ' ': ','
        }

        for key, value in replacements.iteritems():
            res_str = res_str.replace(key, value)

        if kw['export_type'] in ('SHEE', 'EXPO'):

            return request.make_response(
                res_str,
                [
                    ('Content-Type', 'application/ms-excel; charset=UTF-8'),
                    ('Content-Disposition', content_disposition('ptu.xls'))
                ]
            )

        return res_str