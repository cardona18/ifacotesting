# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from dateutil import tz
import codecs
import locale
import logging
import os
import pyodbc
import requests
import subprocess
import sys
import urllib
import uuid
import re

from openerp import fields, models, api
from odoo.exceptions import UserError
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

from num2words import Numero_a_Texto

_logger = logging.getLogger(__name__)

class hr_lot_report_wizard(models.TransientModel):
    _name = 'hr.lot.report.wizard'
    _description = 'HR LOT REPORT WIZARD'

    report = fields.Selection(
        string='Reporte',
        size=10,
        required=True,
        selection=[
            ('POLICY', 'Póliza'),
            ('BANK', 'Depositos en banco'),
            ('TOTAL', 'Auxiliar de nómina'),
            ('EXTRA', 'Retenciones extra'),
            ('PRE_LIST', 'Pre-lista')
        ]
    )
    rtype = fields.Selection(
        string='Tipo',
        size=5,
        default='pdf',
        selection=[
            ('pdf', 'PDF'),
            ('txt', 'Texto')
        ]
    )
    lot_id = fields.Many2one(
        string='Lote',
        comodel_name='hr.paysheet.lot'
    )
    txt_content = fields.Text(
        string='TXT'
    )
    policy_num = fields.Integer(
        string='Número',
        default=1
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

    @api.onchange('lot_id')
    def change_lot_id(self):
        self.company_id = self.lot_id.company_id.id

    @api.multi
    def generate_report(self):

        default_parameters = {
            'company_id': self.lot_id.company_id.id,
            'company_name': self.lot_id.company_id.name,
            'lot_id': self.lot_id.id,
            'from_date': self.locale_format(self.parse_date(self.lot_id.from_date, True), '%d/%b/%Y'),
            'to_date': self.locale_format(self.parse_date(self.lot_id.to_date, True), '%d/%b/%Y'),
            'current_date': self.locale_format(self.current_date(), '%B %d, %Y')
        }

        if self.report == 'POLICY':

            if self.lot_id.state == 'draft':

                self.lot_id.policy_ids.unlink()
                lines = self.policy_lines()

                for account in lines:

                    for segment in lines[account]['segments']:

                        self.env['hr.lot.policy'].create({
                            'name': lines[account]['name'],
                            'credit_amount': lines[account]['segments'][segment]['A'],
                            'debit_amount': lines[account]['segments'][segment]['C'],
                            'account': account,
                            'lot_id': self.lot_id.id,
                            'segment_code': segment,
                            'cash_flow': lines[account]['flow']
                        })

                self.env.cr.commit()

            if self.rtype == 'txt':
                file = self.generate_txt_policy()
                return {
                    'type' : 'ir.actions.act_url',
                    'url': '/web/download/raw_file/?path=%s&_type=%s&filename=%s' % (urllib.quote_plus(file), urllib.quote_plus('text/plain; charset=iso-8859-1'), 'PNOM_%s.txt' % self.lot_id.company_id.short_name),
                    'target': 'self',
                }

            report = self.env['ireport.report'].sudo().search([('code','=','LOT_POLICY')], limit=1)

            if not report.id:
                return

            out_name = 'POLIZA_%s' % self.lot_id.company_id.short_name

            report.setParameters(default_parameters)
            report.addParam('out_name', out_name)
            report.addParam('format', self.rtype)

        if self.report == 'BANK':

            if(self.rtype == 'txt'):
                file = self.generate_txt_bank()
                return {
                    'type' : 'ir.actions.act_url',
                    'url': '/web/download/raw_file/?path=%s&_type=%s&filename=%s' % (urllib.quote_plus(file), urllib.quote_plus('text/plain; charset=iso-8859-1'), 'DEP_%s.txt' % self.lot_id.company_id.short_name),
                    'target': 'self',
                }

            report = self.env['ireport.report'].sudo().search([('code','=','BANK_PAYSHEET')], limit=1)

            if not report.id:
                return

            out_name = 'BANCO_%s' % self.lot_id.company_id.short_name

            report.setParameters(default_parameters)
            report.addParam('bank_account', self.lot_id.company_id.payment_account_id.acc_number)
            report.addParam('out_name', out_name)
            report.addParam('format', self.rtype)

            # AMOUNT TO TEXT
            self.env.cr.execute("""
                SELECT COALESCE(SUM(t.perceptions - t.deductions), 0) AS total_amount FROM (SELECT (
                    SELECT COALESCE(SUM(ABS(amount)), 0)
                        FROM hr_paysheet_trade pt
                        INNER JOIN hr_paysheet hp ON pt.paysheet_id = hp.id
                        INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                        WHERE pc.ctype = 'PER'
                        AND pc.printable = TRUE
                        AND (pantry_card = FALSE OR pantry_card IS NULL)
                        AND hp.lot_id = {0}
                        AND hp.employee_id = he.id
                    ) AS perceptions,
                    (
                        SELECT COALESCE(SUM(ABS(amount)), 0)
                        FROM hr_paysheet_trade pt
                        INNER JOIN hr_paysheet hp ON pt.paysheet_id = hp.id
                        INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                        WHERE pc.ctype = 'DED'
                        AND pc.printable = TRUE
                        AND hp.lot_id = {0}
                        AND hp.employee_id = he.id
                    ) AS deductions
                    FROM hr_paysheet hp
                    INNER JOIN hr_employee he ON hp.employee_id = he.id
                    INNER JOIN resource_resource rr ON he.resource_id = rr.id
                    WHERE hp.lot_id = {0} AND rr.company_id = {1} AND he.payment_type = 'D'
                    ORDER BY he.name_related
                ) AS t
            """.format(self.lot_id.id, self.lot_id.company_id.id))
            report.addParam('amount_string', self.num2text(self.env.cr.fetchone()[0]))

        if self.report == 'EXTRA':

            report = self.env['ireport.report'].sudo().search([('code','=','RETENCIONES_EXTRA')], limit=1)

            if not report.id:
                return

            out_name = 'RET_EXTRA_%s' % self.lot_id.company_id.short_name

            report.setParameters(default_parameters)
            report.addParam('out_name', out_name)

        if self.report == 'TOTAL':

            report = self.env['ireport.report'].sudo().search([('code','=','PAYSHEET_AUX')], limit=1)

            if not report.id:
                return

            out_name = 'AUX_%s' % self.lot_id.company_id.short_name

            report.setParameters(default_parameters)

            if self.employer_id:
                report.addParam('employer_id', "AND he.employer_registration = %s" % self.employer_id.id)
                report.addParam('employer_id_totals', "AND he1.employer_registration = %s" % self.employer_id.id)

            report.addParam('current_date', self.locale_format(self.current_date(), '%B %d, %Y'))
            report.addParam('out_name', out_name)

        if self.report == 'PRE_LIST':

            report = self.env['ireport.report'].sudo().search([('code','=','EMPLOYEE_PRE_LIST')], limit=1)

            if not report.id:
                return

            out_name = 'PRE_LISTA_%s' % self.lot_id.company_id.short_name

            report.setParameters(default_parameters)
            report.addParam('current_date', self.locale_format(self.current_date(), '%B %d, %Y'))
            report.addParam('employer_id', self.employer_id.id)
            report.addParam('out_name', out_name)

        report_file  = report.build()
        report_file += '/%s.pdf' % out_name

        if os.path.isfile(report_file) and os.access(report_file, os.R_OK):
            return {
                'type' : 'ir.actions.act_url',
                'url': '/web/ireport/download_manager?path=%s&type=%s' % (urllib.quote_plus(report_file), 'pdf'),
                'target': 'new'
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

    def current_date(self, _time_zone = "America/Mexico_City"):

        # SET TIME ZONE
        os.environ['TZ'] = _time_zone

        return datetime.today()

    def parse_date(self, _date, _time_zone = "America/Mexico_City"):

        # CURRENT DATE
        return datetime.strptime(_date, DEFAULT_SERVER_DATE_FORMAT)

    # BASE PHP COMMAND
    BASE_COMMAND = 'php /opt/php_files'

    def policy_lines(self):

        # COMPANY CONFIG
        company = self.lot_id.company_id
        cflow = company.cash_flow
        bflow = company.bank_flow
        cash_account = str(company.cash_account_id.code)
        bank_account = str(company.bank_account_id.code)
        lines = {}
        movements = []

        # FIND SEGMENT ACCOUNTS
        command = '%s/accounts_query.php SEGMENTS %s' % (self.BASE_COMMAND, company.old_db_name)
        segment_accounts = eval(self.execute(command))

        # GENERATE MOVEMENTS
        for paysheet in self.lot_id.paysheet_ids:

            for trade in paysheet.trade_ids:

                config = self.env['hr.old.policy.conf'].sudo().search([
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

                    payment_id = self.env['hr.periodic.payment'].search([
                        ('employee_id', '=', paysheet.employee_id.id),
                        ('concept_id', '=', trade.concept_id.id)
                    ], limit=1)

                    if not payment_id.id:
                        raise UserError('Pago no encontrado E: %s, C: %s' % (paysheet.employee_id.name, trade.concept_id.name))

                    input_id = self.env['hr.paysheet.input'].search([
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
                    'C': 0,
                    'A': 0
                }

            if movement['type'] == 'C':

                if movement['sign'] == '+':
                    lines[movement['account']]['segments'][movement['segment']]['C'] += movement['amount']

                if movement['sign'] == '-':
                    lines[movement['account']]['segments'][movement['segment']]['C'] -= movement['amount']

            if movement['type'] == 'A':

                if movement['sign'] == '+':
                    lines[movement['account']]['segments'][movement['segment']]['A'] += movement['amount']

                if movement['sign'] == '-':
                    lines[movement['account']]['segments'][movement['segment']]['A'] -= movement['amount']


        # SET ACCOUNT NAMES
        account_codes = ','.join([acc_code for acc_code in lines])
        command = '%s/accounts_query.php NAMES %s %s' % (self.BASE_COMMAND, company.old_db_name, account_codes or "-1")
        account_names = eval(self.execute(command))

        for acc_index in account_names:

            if acc_index in lines:
                lines[acc_index]['name'] = account_names[acc_index]

        # ADD CASH FLOW
        if cash_account in lines.keys():
            lines[cash_account]['flow'] = cflow

        if bank_account in lines.keys():
            lines[cash_account]['flow'] = bflow

        return lines


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

        expense_config = self.env['hr.segment.config'].sudo().search([
            ('segment_id','=', employee.expense_id.id),
            '|',
            ('company_id', '=', company.id),
            ('company_id', '=', False)
        ], limit=1)

        if not expense_config.id:
            raise UserError("Gasto contable no configurado: %s" % employee.expense_id.name)

        return str(int(expense_config.base_account) + int_acc)

    @api.multi
    def generate_txt_policy(self):
        """
            Generate TXT paysheet policy
        """

        # SET DEAFULT ENCODING
        reload(sys)
        sys.setdefaultencoding('utf-8')

        txt_content = ''
        from_date = datetime.strptime(self.lot_id.from_date, DEFAULT_SERVER_DATE_FORMAT)
        to_date = datetime.strptime(self.lot_id.to_date, DEFAULT_SERVER_DATE_FORMAT)
        payment_date = datetime.strptime(self.lot_id.payment_date, DEFAULT_SERVER_DATE_FORMAT)
        out_path = '/tmp/odoo_txt/%s' % uuid.uuid4()
        filename = '%s/policy.txt' % out_path
        file_encoded = '%s/policy_encoded.txt' % out_path

        # RETRIEVE LINES

        txt_content += 'P %s 3 %s 1 000 Nómina Semanal   del %s al %s %s%s\r\n' % (
            payment_date.strftime('%Y%m%d'),
            str(self.policy_num).zfill(8),
            self.locale_format(from_date, '%d/%b/%Y', True),
            self.locale_format(to_date, '%d/%b/%Y', True),
            ' ' * 53,
            '01 2 '
        )

        for line in self.env['hr.lot.policy'].sudo().search([('lot_id', '=', self.lot_id.id)], order="account"):

            txt_content += 'N %s\r\n' % str(line.segment_code).rjust(4) if line.segment_code else ''

            if abs(line.debit_amount) > 0:
                txt_content += 'M {code}{desc} {type}{amount}{flow}             0.00{blank}\r\n'.format(
                    code=str(line.account).ljust(21),
                    flow=str(line.cash_flow or 0).rjust(4),
                    type=1,
                    amount=str("%0.2f" % line.debit_amount).rjust(17),
                    desc='NS%s' % from_date.strftime('%Y%m%d'),
                    blank=' ' * 32
                )

            if abs(line.credit_amount) > 0:
                txt_content += 'M {code}{desc} {type}{amount}{flow}             0.00{blank}\r\n'.format(
                    code=str(line.account).ljust(21),
                    flow=str(line.cash_flow or 0).rjust(4),
                    type=2,
                    amount=str("%0.2f" % line.credit_amount).rjust(17),
                    desc='NS%s' % from_date.strftime('%Y%m%d'),
                    blank=' ' * 32
                )

        self.execute("mkdir -p %s" % out_path)

        f = open(filename, 'w')
        f.write(txt_content)
        f.close()

        # ENCODE FILE
        self.execute('iconv -f utf-8 -t iso-8859-1 "%s" > "%s"' % (filename, file_encoded))

        return file_encoded

    def get_bank_lines(self, _by_name = False):
        """
            Generate paysheet bank lines
        """

        # SET DEAFULT ENCODING AS UTF-8
        reload(sys)
        sys.setdefaultencoding('utf-8')

        query = """
        SELECT * FROM (
            SELECT he.old_id, he.name_related, he.bank_account, (
                SELECT COALESCE(SUM(ABS(amount)), 0)
                FROM hr_paysheet_trade pt
                INNER JOIN hr_paysheet hp ON pt.paysheet_id = hp.id
                INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                WHERE pc.ctype = 'PER'
                AND pc.printable = TRUE
                AND (pantry_card = FALSE OR pantry_card IS NULL)
                AND hp.lot_id = {lot_id}
                AND hp.employee_id = he.id
            ) AS perceptions,
            (
                SELECT COALESCE(SUM(ABS(amount)), 0)
                FROM hr_paysheet_trade pt
                INNER JOIN hr_paysheet hp ON pt.paysheet_id = hp.id
                INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                WHERE pc.ctype = 'DED'
                AND pc.printable = TRUE
                AND hp.lot_id = {lot_id}
                AND hp.employee_id = he.id
            ) AS deductions
            FROM hr_paysheet hp
            INNER JOIN hr_employee he ON hp.employee_id = he.id
            INNER JOIN resource_resource rr ON he.resource_id = rr.id
            WHERE hp.lot_id = {lot_id} AND rr.company_id = {cid} AND he.payment_type = 'D'
            ORDER BY he.name_related
        ) AS totals WHERE (totals.perceptions - totals.deductions) > 0
        """

        self.env.cr.execute(query.format(
            lot_id=self.lot_id.id,
            cid=self.lot_id.company_id.id
        ))

        return self.env.cr.fetchall()

    def num2text(self, num):

        return Numero_a_Texto(num)

    def generate_txt_bank(self):

        # SET DEAFULT ENCODING
        reload(sys)
        sys.setdefaultencoding('utf-8')

        lines = self.get_bank_lines(True)
        count = len(lines)
        total = sum(line[3] - line[4] for line in lines)
        from_date = datetime.strptime(self.lot_id.from_date, DEFAULT_SERVER_DATE_FORMAT)
        to_date = datetime.strptime(self.lot_id.to_date, DEFAULT_SERVER_DATE_FORMAT)
        company = self.lot_id.company_id
        txt_content = ''
        out_path = '/tmp/odoo_txt/%s' % uuid.uuid4()
        filename = '%s/bank.txt' % out_path
        file_encoded = '%s/bank_encoded.txt' % out_path

        desc_str = 'Nom. del {date_from} al {date_to}'.format(
            date_from=self.locale_format(from_date, '%d/%b/%y', True),
            date_to=self.locale_format(to_date, '%d/%b/%y', True)
        ).ljust(34)

        txt_content += 'MXPRLFF%s%s%s%s     %s\r\n' % (
            str(company.payment_account_id.acc_number).zfill(10),
            str('%.2f' % total).replace('.','').zfill(14),
            str(count).zfill(7),
            self.current_date().strftime('%d%m%Y'),
            desc_str
        )

        for line in lines:

            dep_amount = line[3] - line[4]

            txt_content += '{account}{amount}{desc}{employee}{line_end}'.format(
                account=str(line[2]).zfill(10),
                amount=str('%.2f' % (dep_amount) ).replace('.','').zfill(14),
                desc=desc_str,
                employee=line[1][:35].ljust(35),
                line_end='\r\n' if line != lines[-1] else ''
            )

        self.execute("mkdir -p %s" % out_path)

        f = open(filename, 'w')
        f.write(txt_content)
        f.close()

        # ENCODE FILE
        self.execute('iconv -f utf-8 -t iso-8859-1 "%s" > "%s"' % (filename, file_encoded))

        return file_encoded

    def get_extra_retention_lines(self):
        """
            Generate paysheet bank lines
        """

        query = """
            SELECT * FROM (
                SELECT he.old_id, he.name_related, (
                    SELECT COALESCE(SUM(ABS(amount)), 0)
                    FROM hr_paysheet_trade pt
                    INNER JOIN hr_paysheet hp ON pt.paysheet_id = hp.id
                    INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                    WHERE pc.ctype = 'PER'
                    AND pc.printable = TRUE
                    AND hp.lot_id = {lot_id}
                    AND hp.employee_id = he.id
                ) AS perceptions,
                (
                    SELECT COALESCE(SUM(ABS(amount)), 0)
                    FROM hr_paysheet_trade pt
                    INNER JOIN hr_paysheet hp ON pt.paysheet_id = hp.id
                    INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                    WHERE pc.ctype = 'DED'
                    AND pc.printable = TRUE
                    AND hp.lot_id = {lot_id}
                    AND hp.employee_id = he.id
                ) AS deductions,
                (
                    SELECT COALESCE(SUM(ABS(amount)), 0)
                    FROM hr_paysheet_trade pt
                    INNER JOIN hr_paysheet hp ON pt.paysheet_id = hp.id
                    INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                    WHERE pc.code = 48
                    AND hp.lot_id = {lot_id}
                    AND hp.employee_id = he.id
                ) AS savings_fund_lending,
                (
                    SELECT COALESCE(SUM(ABS(amount)), 0)
                    FROM hr_paysheet_trade pt
                    INNER JOIN hr_paysheet hp ON pt.paysheet_id = hp.id
                    INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                    WHERE pc.code = 17
                    AND hp.lot_id = {lot_id}
                    AND hp.employee_id = he.id
                ) AS savings_fund,
                (
                    SELECT COALESCE(SUM(ABS(amount)), 0)
                    FROM hr_paysheet_trade pt
                    INNER JOIN hr_paysheet hp ON pt.paysheet_id = hp.id
                    INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
                    WHERE pc.code = 15
                    AND hp.lot_id = {lot_id}
                    AND hp.employee_id = he.id
                ) AS pantry
                FROM hr_paysheet hp
                INNER JOIN hr_employee he ON hp.employee_id = he.id
                INNER JOIN resource_resource rr ON he.resource_id = rr.id
                WHERE hp.lot_id = {lot_id}
                ORDER BY he.name_related
            ) AS totals WHERE totals.savings_fund > 0
        """

        self.env.cr.execute(query.format(
            lot_id=self.lot_id.id
        ))

        return self.env.cr.fetchall()

    def currency_format(self, _amount, _locale = 'es_MX.UTF-8'):

        # Convenrt date to locale format
        locale.setlocale(locale.LC_ALL, _locale)

        return locale.currency(_amount, grouping=True)

    def get_total_lines(self, _type = False):

        query = """
            SELECT pc.name, COALESCE(SUM(ABS(amount)), 0)
            FROM hr_paysheet_trade pt
            INNER JOIN hr_paysheet hp ON pt.paysheet_id = hp.id
            INNER JOIN hr_paysheet_concept pc ON pt.concept_id = pc.id
            WHERE %s
            AND pc.report_print = TRUE
            AND hp.lot_id = %s
            GROUP BY pc.name, pc.code
            ORDER BY pc.code
        """

        cfilter = "pc.ctype = '%s'" % _type if _type else "pc.ctype != 'DED' AND pc.ctype != 'PER'"

        self.env.cr.execute(query % (cfilter, self.lot_id.id))

        return self.env.cr.fetchall()

    def execute(self, _command):
        try:
            return subprocess.check_output(_command, shell=True, stderr=subprocess.STDOUT)
        except Exception, e:
            _logger.error('EXECUTE ERROR: %s', e)