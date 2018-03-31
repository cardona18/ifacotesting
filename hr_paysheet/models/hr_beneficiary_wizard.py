# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
import logging
import subprocess
import urllib
import uuid

from openerp import fields, models, api
from openerp.osv.orm import except_orm

_logger = logging.getLogger(__name__)

class hr_beneficiary_wizard(models.TransientModel):
    _name = 'hr.beneficiary.wizard'
    _description = 'HR BENEFICIARY WIZARD'

    from_date = fields.Date(
        string='Desde',
        default=datetime.today()
    )
    all_employees = fields.Boolean(
        string='Todos los empleados',
        default=False
    )

    @api.multi
    def export_file(self):

        file_header = ''
        file_contents = ''
        out_path = '/tmp/odoo_txt/'
        filename = '%s/%s.txt' % (out_path, uuid.uuid4())
        employees = self.env['hr.employee'].search([('payment_type','=','D')] if self.all_employees else [('payment_type','=','D'), ('in_date','>=',self.from_date)])
        num_accounts = 0
        current_date = datetime.today()

        file_header += 'AUTHBENEH,ABCXXXXXXXX,MX-%s,,,,{num_lines},{num_accounts}\r\n' % str('%s%s%s%s%s%s%s' % (
            current_date.year,
            current_date.month,
            current_date.day,
            current_date.hour,
            current_date.minute,
            current_date.second,
            current_date.microsecond
        ))[:32]

        for employee in employees:

            contract = self.env['hr.contract'].search([
                ('company_id','=',employee.company_id.id),
                ('employee_id','=',employee.id),
                ('for_paysheet','=',True)
            ], limit=1)

            if not contract:
                _logger.info("SIN CONTRATO - %s" % (employee.name))
                continue

            if not employee.bank_account:
                raise except_orm('ERROR','%s NO TIENE ESTABLECIDA UNA CUENTA BANCARIA' % employee.name)

            if not employee.beneficiary_code:
                employee.beneficiary_code = 'A%s' % employee.bank_account

            file_contents += 'BENEDET,%s,%s,,,,MXOP,A,MX,%s,L,%s,BID\r\n' % (
                employee.beneficiary_code,
                employee.name
                .replace('Ñ','N')
                .replace('ñ','n')
                .replace('Á','A')
                .replace('É','E')
                .replace('Í','I')
                .replace('Ó','O')
                .replace('Ú','U')
                .replace('á','a')
                .replace('é','e')
                .replace('í','i')
                .replace('ó','o')
                .replace('ú','u')[:35],
                employee.bank_account,
                employee.bank_id.bic
            )

            num_accounts += 1

        self.execute("mkdir -p %s" % out_path)

        f = open(filename, 'w')
        f.write('%s%s' %  (file_header.format(**{
            'num_lines': num_accounts + 1,
            'num_accounts': num_accounts,
        }), file_contents))
        f.close()

        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/download/raw_file/?path=%s&_type=%s&filename=%s' % (urllib.quote_plus(filename), urllib.quote_plus('text/plain; charset=utf-8'), 'beneficiarios.csv'),
            'target': 'self',
        }

    def execute(self, _command):
        try:
            return subprocess.check_output(_command, shell=True, stderr=subprocess.STDOUT)
        except Exception, e:
            _logger.error('EXECUTE ERROR: %s', e)