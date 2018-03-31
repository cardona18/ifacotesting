# -*- coding: utf-8 -*-
# © <2017> <Omar Torres (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import cStringIO
import csv

from odoo import fields, models, api

class hr_cfdi_cancel_wizard(models.TransientModel):
    _name = 'hr.cfdi.cancel.wizard'
    _description = 'HR CFDI CANCEL WIZARD'

    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company'
    )
    csv_file = fields.Binary(
        string='Listado (CSV)'
    )
    csv_filename = fields.Char(
        string='Archivo'
    )
    cancel_nf = fields.Boolean(
        string='Cancelar no encontrados',
        help='Intentar cancelar UUID no encontrados en la base de datos local'
    )
    cancel_log = fields.Text(
        string='Log'
    )
    state = fields.Selection(
        string='Estado',
        default='L',
        selection=[
            ('L', 'Listado'),
            ('R', 'Resultado')
        ]
    )

    @api.multi
    def cfdi_cancel(self):

        file_content = self.csv_file.decode('base64')
        file_lines = cStringIO.StringIO(file_content)
        csv_lines = list(csv.reader(file_lines, delimiter=','))
        line_count = 0
        result_log = ''

        sign_task = self.env['cfdi.sign.task'].sudo().create({
            'company_id': self.company_id.id
        })
        sign_task.prepare_ws_config()

        for csv_line in csv_lines:

            cfdi_name = csv_line[0].strip().upper()

            # SEARCH IN DATABASE

            cfdi = self.env['hr.xml.cfdi'].search([('name', '=', cfdi_name)])
            result_log += '%s: %s localmente.\n' % (cfdi_name, 'Encontrado' if cfdi.id else 'No encontrado')

            if not cfdi.id and not self.cancel_nf:
                continue

            # TRY CANCEL
            response = sign_task.cfdi_cancel(cfdi_name)

            if response.result:
                result_log += '%s: Cancelado.\n' % cfdi_name

                if cfdi.id:
                    cfdi.state = 'canceled'

            else:
                result_log += '{0}: {1} - {2}\n'.format(cfdi_name, response.error_code, response.error)

        self.state = 'R'
        self.cancel_log = result_log

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.cfdi.cancel.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }