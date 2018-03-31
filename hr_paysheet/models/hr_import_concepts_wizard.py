# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import sys
import cStringIO
import base64
import csv

from openerp import fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class hr_import_concepts_wizard(models.TransientModel):
    _name = 'hr.import.concepts.wizard'
    _description = 'HR IMPORT CONCEPTS WIZARD'

    import_type = fields.Selection(
        string='Importar',
        size=3,
        selection=[
            ('TXT', 'Tiempo trabajado'),
            ('CSV', 'Archivo (CSV)')
        ]
    )
    b64_file = fields.Binary(
        string='Archivo TXT'
    )
    csv_file = fields.Binary(
        string='Archivo CSV',
        help="Formato (EMPRESA,CLAVE_EMPLEADO,CLAVE_CONCEPTO,CANTIDAD)"
    )
    apply_date = fields.Date(
        string='Fecha',
        required=True
    )
    replace_type = fields.Selection(
        string='Existentes',
        size=3,
        default='UPD',
        selection=[
            ('UPD', 'Actualizar'),
            ('REP', 'Remplazar')
        ]
    )
    import_zero = fields.Boolean(
        string='Importar en cero',
        default=False
    )

    @api.multi
    def import_file(self):

        # change the default encoding to utf-8
        reload(sys)
        sys.setdefaultencoding('utf-8')

        if self.import_type == 'TXT':

            file_content = self.b64_file.decode('base64')
            file_lines = self.txt2csv(file_content)

        if self.import_type == 'CSV':

            file_content = self.csv_file.decode('base64')
            file_lines = cStringIO.StringIO(file_content)

        self.import_csv(file_lines)

    def import_csv(self, lines):

        csv_lines = list(csv.reader(lines, delimiter=','))
        line_count = 0

        for csv_line in csv_lines:

            company = self.env['res.company'].search([('short_name', '=', csv_line[0])], limit=1)

            if not company.id:
                _logger.debug('EMPRESA NO ENCONTRADA: %s' % csv_line[0])
                continue

            employee = self.env['hr.employee'].search([
                ('old_id', '=', csv_line[1]),
                ('company_id', '=', company.id)
            ], limit=1)

            if not employee.id:
                _logger.debug('EMPLEADO NO ENCONTRADO: %s/%s' % (csv_line[0], csv_line[1]))
                continue

            contract = self.env['hr.contract'].search([
                ('employee_id', '=', employee.id),
                ('company_id', '=', company.id),
                ('for_paysheet', '=', True)
            ], limit=1)

            if not contract.id:
                _logger.debug('EMPLEADO SIN CONTRATO: %s/%s' % (csv_line[0], csv_line[1]))
                continue

            concept = self.env['hr.paysheet.concept'].search([
                ('code', '=', csv_line[2])
            ], limit=1)

            if not concept.id:
                _logger.debug('CONCEPTO NO ENCONTRADO: %s' % csv_line[2])
                continue

            try:
                amount = float(csv_line[3])
            except Exception as e:
                raise UserError('ERROR DE FORMATO: %s => %s' % (line_count, csv_line[3]))

            if not self.import_zero and amount == 0:
                continue

            payment_id = self.env['hr.periodic.payment'].search([
                ('employee_id', '=', employee.id),
                ('concept_id', '=', concept.id)
            ])

            if payment_id.id and self.replace_type == 'UPD':
                payment_id.amount = amount
                payment_id.apply_date = self.apply_date
                continue

            if payment_id.id and self.replace_type == 'REP':
                payment_id.unlink()

            self.env['hr.periodic.payment'].create({
                'employee_id': employee.id,
                'company_id': company.id,
                'concept_id': concept.id,
                'amount': amount,
                'apply_date': self.apply_date
            })

            line_count += 1

    def txt2csv(self, lines):

        WORK_LENGTH = 120
        CONCEPT_LENGTH = 69
        WORK_DAYS_CONCEPT = 34
        EXTRA_TIME_CONCEPT = 78

        res = ''
        line_count = 0
        pre_result = {}

        for line in cStringIO.StringIO(lines):

            line_len = len(line)
            line_count += 1
            company = line[4:7].strip()
            employee = int(line[8:13].strip())

            if company not in pre_result:
                pre_result[company] = {}

            if employee not in pre_result[company]:
                pre_result[company][employee] = {}

            if line_len == WORK_LENGTH:

                if WORK_DAYS_CONCEPT not in pre_result[company][employee]:
                    pre_result[company][employee][WORK_DAYS_CONCEPT] = line[76:80].strip()

                if EXTRA_TIME_CONCEPT not in pre_result[company][employee]:
                    pre_result[company][employee][EXTRA_TIME_CONCEPT] = line[56:59].strip() or '0'

                continue


            if line_len == CONCEPT_LENGTH:

                concept_code = int(line[49:58].strip())
                concept_amount = float(line[59:].strip())

                if concept_code not in pre_result[company][employee]:
                    pre_result[company][employee][concept_code] = concept_amount
                    continue

                pre_result[company][employee][concept_code] += concept_amount

        # CONVERT LINES
        for company in pre_result:

            for employee in pre_result[company]:

                for concept in pre_result[company][employee]:

                    res += '{0},{1},{2},{3}\n'.format(company, employee, concept, pre_result[company][employee][concept])

        return cStringIO.StringIO(res)