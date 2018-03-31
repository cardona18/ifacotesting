# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import os
import sys
import locale
import base64

from openerp import http
from openerp.addons.web.controllers.main import serialize_exception,content_disposition
from openerp.http import request

_logger = logging.getLogger(__name__)

class TimecheckMonitor(http.Controller):

    @http.route('/web/export_time/timechecks', type='http', auth="user")
    @serialize_exception
    def time_checks_export(self, **kw):
        """@returns: :class:`werkzeug.wrappers.Response`"""

        # SET DEAFULT ENCODING AS UTF-8
        reload(sys)
        sys.setdefaultencoding('utf-8')

        # SET LOCALE
        locale.setlocale(locale.LC_ALL, 'es_MX.UTF-8')

        period_id = http.request.env['hr.work.period'].browse(int(kw['pid']))

        http.request.env.cr.execute("""
            SELECT employee_id, sum(worked_hours) AS worked_hours, ht.work_hours, he.add_saturday, sum(extra_hours) AS extra_hours, he.name_related
            FROM hr_timecheck_workday wd
            INNER JOIN hr_timecheck_turn ht ON wd.turn_id = ht.id
            INNER JOIN hr_employee he ON wd.employee_id = he.id
            WHERE period_id = {0}
            GROUP BY employee_id, ht.work_hours, he.add_saturday
        """.format(period_id.id))

        worked_hours = http.request.env.cr.fetchall()

        work_lines = {}

        for employee_hours in worked_hours:

            # holiday_ids = http.request.env['hr.holidays.request'].search([
            #     ('employee_id', '=', employee_hours[0]),
            #     ('from_time', '<=', period_id.from_date),
            #     ('to_time', '>=', period_id.from_date),
            #     '|',
            #     ('from_time', '<=', period_id.to_date),
            #     ('to_time', '>=', period_id.to_date)
            # ])

            # absence_ids = http.request.env['hr.absence'].search([
            #     ('employee_id', '=', employee_hours[0]),
            #     ('from_date', '<=', period_id.from_date),
            #     ('to_date', '>=', period_id.from_date),
            #     '|',
            #     ('from_date', '<=', period_id.to_date),
            #     ('to_date', '>=', period_id.to_date)
            # ])

            # disability_ids = http.request.env['hr.holidays.request'].search([
            #     ('employee_id', '=', employee_hours[0]),
            #     ('from_date', '<=', period_id.from_date),
            #     ('to_date', '>=', period_id.from_date),
            #     '|',
            #     ('from_date', '<=', period_id.to_date),
            #     ('to_date', '>=', period_id.to_date)
            # ])

            work_lines[employee_hours[0]] = {
                'work_days': employee_hours[1] / float(employee_hours[2]) + 1 if employee_hours[3] else 0,
                'extra_time': employee_hours[4],
                'employee': employee_hours[5]
            }


        if kw['type'] in ('PR','SH'):

            res_str = '<table%scellpadding="0" width="900px">' % (' border="1" ' if kw['type'] == 'PR' else ' ')

            res_str += '<tr bgcolor="B0CBF0">'
            res_str += '<td>Empleado</td><td>Días trabajados</td><td>Horas extra</td>'
            res_str += '</tr>'

            for line in work_lines:

                row_str  = '<tr>'
                row_str += '<td>%s</td><td align="right">%s</td><td align="right">%s</td>'
                row_str += '</tr>'

                res_str += row_str % (
                    line['employee'],
                    "{:,.2f}".format(line['work_days']),
                    "{:,.2f}".format(line['extra_time'])
                )

            res_str += '</table>'


        if kw['type'] == 'PS':

            res_str = ''

            for line in http.request.env['hr.work.period.tmp'].search([('period_id', '=', int(kw['pid']))]):

                base_row_str = '%s,%s,' % (
                    line.employee_id.company_id.short_name,
                    line.employee_id.old_id
                )

                res_str += "%s%s\n%s%s\n" % (
                    base_row_str,
                    '%s,%s' % (
                        34,
                        "{:,.2f}".format(line.work_days)
                    ),
                    base_row_str,
                    '%s,%s' % (
                        78,
                        "{:,.2f}".format(line.extra_time)
                    )
                )

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

        if kw['type'] in ('PS'):

            return request.make_response(
                base64.b64encode(bytes(res_str)),
                [
                    ('Content-Type', 'text/plain; charset=UTF-8'),
                    ('Content-Disposition', content_disposition('tiempo_trabajado.tt'))
                ]
            )

        if kw['type'] in ('SH'):

            return request.make_response(
                res_str,
                [
                    ('Content-Type', 'application/vnd.oasis.opendocument.spreadsheet; charset=UTF-8'),
                    ('Content-Disposition', content_disposition('tiempo_trabajado.ods'))
                ]
            )

        return res_str