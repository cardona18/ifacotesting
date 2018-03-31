# -*- coding: utf-8 -*-

import os
import urllib
import logging
import subprocess

from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import serialize_exception,content_disposition

_logger = logging.getLogger(__name__)

class HRReports(http.Controller):

    # BASE PHP COMMAND
    BASE_COMMAND = 'php /opt/php_files'

    @http.route('/hr_reports/policy_check', type='http')
    @serialize_exception
    def report_policy_check(self, **kw):
        """ @returns: :class:`werkzeug.wrappers.Response` """

        lot_id = http.request.env['hr.paysheet.lot'].sudo().browse(int(kw['lot_id']))

        if not lot_id:
            return 'LOT NOT FOUND'

        # COMPANY CONFIG
        company = lot_id.company_id
        cash_account = str(company.cash_account_id.code)
        bank_account = str(company.bank_account_id.code)
        lines = {}
        movements = []

        # FIND SEGMENT ACCOUNTS
        command = '%s/accounts_query.php SEGMENTS %s' % (self.BASE_COMMAND, company.old_db_name)
        segment_accounts = eval(self.execute(command))

        # GENERATE MOVEMENTS
        for paysheet in lot_id.paysheet_ids:

            for trade in paysheet.trade_ids:

                config = http.request.env['hr.old.policy.conf'].sudo().search([
                    ('concept_id', '=', trade.concept_id.id),
                    '|',
                    ('company_id', '=', company.id),
                    ('company_id', '=', False)
                ], limit=1)

                if not config:
                    continue

                account1 = self.check_account(str(config.account1), paysheet.employee_id, company)
                account2 = self.check_account(str(config.account2), paysheet.employee_id, company)
                amount = abs(trade.amount)
                segmen_code = int(paysheet.employee_id.segment_id.code)

                if account1 == -2 or account2 == -2:

                    payment_id = http.request.env['hr.periodic.payment'].search([
                        ('employee_id', '=', paysheet.employee_id.id),
                        ('concept_id', '=', trade.concept_id.id)
                    ], limit=1)

                    if not payment_id.id:
                        raise UserError('Pago no encontrado E: %s, C: %s' % (paysheet.employee_id.name, trade.concept_id.name))

                    input_id = http.request.env['hr.paysheet.input'].search([
                        ('paysheet_id', '=', paysheet.id),
                        ('concept_id', '=', trade.concept_id.id)
                    ], limit=1)

                    if not input_id.id:
                        raise UserError('Entrada no encontrada P: %s, C: %s' % (paysheet.name, trade.concept_id.name))

                    # UPDATE INPUT ACCOUNTS
                    input_id.account1_id = payment_id.account1_id.id
                    input_id.account2_id = payment_id.account2_id.id

                    if account1 == -2 and not input_id.account1_id.id:
                        raise UserError('Cuenta no encontrada P: %s, I: %s' % (paysheet.name, input_id.code))

                    if account2 == -2 and not input_id.account2_id.id:
                        raise UserError('Contra cuenta no encontrada P: %s, I: %s' % (paysheet.name, input_id.code))

                    account1_id = input_id.account1_id
                    account2_id = input_id.account2_id

                    if account1_id.id:

                        movements.append({
                            'segment': segmen_code if int(account1_id.account) in segment_accounts else 0,
                            'account': str(account1_id.account),
                            'type': account1_id.mtype,
                            'sign': account1_id.sign,
                            'amount': amount
                        })

                    if account2_id.id:

                        movements.append({
                            'segment': segmen_code if int(account2_id.account) in segment_accounts else 0,
                            'account': str(account2_id.account),
                            'type': account2_id.mtype,
                            'sign': account2_id.sign,
                            'amount': amount
                        })

                int_account1 = int(account1)
                int_account2 = int(account2)

                if int_account1 not in (0,-2):

                    movements.append({
                        'segment': segmen_code if int_account1 in segment_accounts else 0,
                        'account': str(account1),
                        'type': config.type1,
                        'sign': config.sign1,
                        'amount': amount
                    })

                if int_account2 not in (0,-2):

                    movements.append({
                        'segment': segmen_code if int_account2 in segment_accounts else 0,
                        'account': str(account2),
                        'type': config.type2,
                        'sign': config.sign2,
                        'amount': amount
                    })


        # GENERATE POLICY LINES
        for movement in movements:

            if movement['account'] not in lines.keys():

                lines[movement['account']] = {
                    'segments': {},
                    'name': '',
                    'flow': ''
                }

            if movement['segment'] not in lines[movement['account']]['segments'].keys():

                lines[movement['account']]['segments'][movement['segment']] = {
                    'CP': 0,
                    'CN': 0,
                    'AP': 0,
                    'AN': 0
                }

            if movement['type'] == 'C':

                if movement['sign'] == '+':
                    lines[movement['account']]['segments'][movement['segment']]['CP'] += movement['amount']

                if movement['sign'] == '-':
                    lines[movement['account']]['segments'][movement['segment']]['CN'] += movement['amount']

            if movement['type'] == 'A':

                if movement['sign'] == '+':
                    lines[movement['account']]['segments'][movement['segment']]['AP'] += movement['amount']

                if movement['sign'] == '-':
                    lines[movement['account']]['segments'][movement['segment']]['AN'] += movement['amount']

        res_str = '<table border="1" cellpadding="0" width="7000px">'

        res_str += '<tr bgcolor="B0CBF0">'
        res_str += '<td>Cuenta</td><td>Abono Positivo</td><td>Abono Negativo</td><td>Cargo Positivo</td><td>Cargo Negativo</td>'
        res_str += '</tr>'

        for account in lines:

            for segment in lines[account]['segments']:


                row_str  = '<tr>'
                row_str += '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>'
                row_str += '</tr>'


                res_str += row_str % (
                    account,
                    lines[account]['segments'][segment]['AP'],
                    lines[account]['segments'][segment]['AN'],
                    lines[account]['segments'][segment]['CP'],
                    lines[account]['segments'][segment]['CN']
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

        return request.make_response(
            res_str,
            [
                ('Content-Type', 'application/ms-excel; charset=UTF-8'),
                ('Content-Disposition', content_disposition('poliza_nomina_movimientos.xls'))
            ]
        )

    def check_account(self, account, employee, company):

        if len(account) > 4:
            return account

        int_acc = int(account)

        if int_acc in (0,-2):
            return int_acc

        if int_acc == -1:

            if not company.bank_account_id.id or not company.cash_account_id.id:
                raise UserError("Cuenta de banco no configurada para la empresa: %s" % company.name)

            if employee.payment_type == 'D':
                return str(company.bank_account_id.code)

            if employee.payment_type == 'E':
                return str(company.cash_account_id.code)

            raise UserError('No es posible determinar la cuenta de pago: {0}'.format(employee.name))

        if not employee.expense_id.id:
            raise UserError("Empleado sin gasto contable: %s" % employee.name)

        expense_config = http.request.env['hr.segment.config'].sudo().search([
            ('segment_id','=', employee.expense_id.id),
            '|',
            ('company_id', '=', company.id),
            ('company_id', '=', False)
        ], limit=1)

        if not expense_config.id:
            raise UserError("Gasto contable no configurado: %s" % employee.expense_id.name)

        return str(int(expense_config.base_account) + int_acc)


    def execute(self, _command):
        try:
            return subprocess.check_output(_command, shell=True, stderr=subprocess.STDOUT)
        except Exception, e:
            _logger.error('EXECUTE ERROR: %s', e)


    @http.route('/hr_reports/cfdi_errors', type='http')
    @serialize_exception
    def report_cfdi_errors(self, **kw):
        """ @returns: :class:`werkzeug.wrappers.Response` """

        STATE_MAP = {
            'signed': 'Timbrado',
            'canceled': 'Cancelado'
        }

        http.request.env.cr.execute("""
            SELECT rfc_src, rfc_dst, from_date, to_date, payment_date, count(*)
            FROM hr_xml_cfdi
            GROUP BY rfc_src, rfc_dst, from_date, to_date, payment_date, state
            HAVING count(*) > 1 AND state = 'signed'
        """)

        res_str = '<table border="1" cellpadding="0" width="1200px">'
        res_str += '<tr bgcolor="B0CBF0">'
        res_str += '<td>UUID</td><td>Emisor</td><td>Receptor</td><td>Desde</td><td>Hasta</td><td>Fecha de pago</td><td>Estado</td>'
        res_str += '</tr>'

        for dp_row in http.request.env.cr.fetchall():

            http.request.env.cr.execute("""
                SELECT "name", rfc_src, rfc_dst, from_date, to_date, payment_date, state
                FROM hr_xml_cfdi
                WHERE rfc_src = '%s' AND rfc_dst = '%s' AND from_date = '%s' AND to_date = '%s' AND payment_date = '%s'
            """ % (
                dp_row[0],
                dp_row[1],
                dp_row[2],
                dp_row[3],
                dp_row[4]
            ))

            for result in http.request.env.cr.fetchall():

                row_str  = '<tr>'
                row_str += '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>'
                row_str += '</tr>'

                res_str += row_str % (
                    result[0],
                    result[1],
                    result[2],
                    result[3],
                    result[4],
                    result[5],
                    STATE_MAP[result[6]]
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
                    ('Content-Disposition', content_disposition('inconcistencias_cfdi.xls'))
                ]
            )

        return res_str