# -*- coding: utf-8 -*-
# © <2017> <Omar Torres (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import cStringIO
import csv
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class hr_gen_xml_wizard(models.TransientModel):
    _name = 'hr.gen.xml.wizard'
    _description = 'HR GEN XML WIZARD'

    cfdi_action = fields.Selection(
        string='Acción',
        default='G',
        selection=[
            ('G', 'Generar XML'),
            ('S', 'Timbrar')
        ]
    )
    csv_file = fields.Binary(
        string='Listado (CSV)'
    )
    csv_filename = fields.Char(
        string='Archivo'
    )
    process_log = fields.Text(
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
    def gen_xml_files(self):

        file_content = self.csv_file.decode('base64')
        file_lines = cStringIO.StringIO(file_content)
        csv_lines = list(csv.reader(file_lines, delimiter=','))
        line_count = 0
        total_count = len(csv_lines)
        result_log = ''

        for csv_line in csv_lines:

            cfdi_name = csv_line[0].strip().upper()

            # SEARCH IN DATABASE

            cfdi = self.env['hr.xml.cfdi'].search([('name', '=', cfdi_name)])

            if not cfdi.id:
                result_log += '%s: No encontrado localmente.\n' % cfdi_name
                continue

            for paysheet_cfdi in cfdi.paysheet_id.cfdi_ids:

                if cfdi_name == paysheet_cfdi.name and paysheet_cfdi.state == 'signed':
                    paysheet_cfdi.state = 'canceled'

            signed_xml_id = cfdi.paysheet_id.cfdi_ids.search([('paysheet_id', '=', cfdi.paysheet_id.id), ('state', '=', 'signed')], limit=1)

            if signed_xml_id.id:
                result_log += '%s %s %s: Timbrada.\n' % (cfdi.paysheet_id.lot_id.name, csv_line[2], csv_line[3])
                continue

            if self.cfdi_action == 'G':
                cfdi.paysheet_id.state = 'error'
                cfdi.paysheet_id.generate_xml()
            else:
                cfdi.paysheet_id.action_sign()
                self.env.cr.commit()

            result_log += 'Paysheet %s: %s\n' % (cfdi.paysheet_id.id, cfdi.paysheet_id.state)
            _logger.debug('Paysheet %s: %s', cfdi.paysheet_id.id, cfdi.paysheet_id.state)

            if line_count % 100 == 0:
                _logger.debug("LINE %s OF %s" % (line_count, total_count))

            line_count += 1

        self.state = 'R'
        self.process_log = result_log

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }