# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import requests
import subprocess
import urllib
import uuid

from openerp import fields, models, api
from openerp.osv.orm import except_orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)

class hr_export_rfc_wizard(models.TransientModel):
    _name = 'hr.export.rfc.wizard'
    _description = 'HR EXPORT RFC WIZARD'

    export_type = fields.Selection(
        string='Exportar',
        default='ALL',
        size=3,
        selection=[
            ('ALL', 'Todos'),
            ('DAT', 'Por fecha de alta')
        ]
    )
    enc_type = fields.Selection(
        string='Codificación',
        default='8859',
        size=4,
        selection=[
            ('8859', 'ISO-8859-1'),
            ('UTF8', 'UTF-8')
        ]
    )
    from_date = fields.Date(
        string='Fecha de alta'
    )
    inactive = fields.Boolean(
        string='Empleados inactivos'
    )
    emp_name = fields.Boolean(
        string='Nombre del empleado'
    )

    @api.multi
    def export_action(self):

        txt_content = ''
        out_path = '/tmp/odoo_txt/%s' % uuid.uuid4()
        filename = '%s/tmp.txt' % out_path
        file_encoded = '%s/tmp_encoded.txt' % out_path
        export_file = ''
        export_charset = ''
        domain = [('old_id', '>', 0)]

        if self.export_type == 'DAT':
            domain += [('reg_date', '>=', self.from_date)]

        if self.inactive:
            domain += ['|', ('active', '=',True), ('active', '=', False)]

        employees = self.env['hr.employee'].search(domain)

        if not len(employees):
            raise exept_orm('NF001', 'No se encontraron registros')

        i = 1

        for employee in employees:

            contract = self.env['hr.contract'].search([
                ('employee_id', '=', employee.id),
                ('for_paysheet', '=', True),
                '|',
                ('active', '=',True),
                ('active', '=', False)
            ], limit=1)

            if not contract.id:
                _logger.debug("CONTRACT NOT FOUND: %s", employee.id)
                continue

            txt_content += '%s%s|%s\r\n' % (
                '%s|' % employee.name if self.emp_name else '',
                i,
                employee.rfc
            )

            i += 1

        self.execute("mkdir -p %s" % out_path)

        f = open(filename, 'w')
        f.write(txt_content)
        f.close()

        if self.enc_type == '8859':
            self.execute('iconv -f utf-8 -t iso-8859-1 "%s" > "%s"' % (filename, file_encoded))
            export_file = file_encoded
            export_charset = 'iso-8859-1'
        else:
            export_file = filename
            export_charset = 'utf-8'

        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/download/raw_file/?path=%s&_type=%s&filename=%s' % (
                urllib.quote_plus(export_file),
                urllib.quote_plus('text/plain; charset=%s' % export_charset),
                'RFC.txt'
            ),
            'target': 'self'
        }


    def execute(self, _command):
        try:
            return subprocess.check_output(_command, shell=True, stderr=subprocess.STDOUT)
        except Exception, e:
            _logger.error('EXECUTE ERROR: %s', e)