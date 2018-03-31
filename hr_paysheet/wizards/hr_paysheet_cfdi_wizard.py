# -*- coding: utf-8 -*-
# © <2017> <Omar Torres (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class hr_paysheet_cfdi_wizard(models.TransientModel):
    _name = 'hr.paysheet.cfdi.wizard'
    _description = 'HR PAYSHEET CFDI WIZARD'

    export_type = fields.Selection(
        string='Exportar',
        size=1,
        selection=[
            ('P', 'Vista previa'),
            ('X', 'XLS')
        ]
    )

    @api.multi
    def check_duplicated_data(self):

        cfdi_ids = ()

        for cfdi in self.env['hr.xml.cfdi'].search([('send_date', '=', False)]):

            xml = cfdi.parse_xml()
            voucher = xml.find('.//{http://www.sat.gob.mx/TimbreFiscalDigital}TimbreFiscalDigital')
            paysheet = xml.find('.//{http://www.sat.gob.mx/nomina12}Nomina')
            src = xml.find('.//{http://www.sat.gob.mx/cfd/3}Emisor')
            dst = xml.find('.//{http://www.sat.gob.mx/cfd/3}Receptor')

            cfdi.write({
                'send_date': xml.get('fecha').replace('T', ' '),
                'cert_date': voucher.get('FechaTimbrado').replace('T', ' '),
                'amount': xml.get('total'),
                'from_date': paysheet.get('FechaInicialPago'),
                'to_date': paysheet.get('FechaFinalPago'),
                'payment_date': paysheet.get('FechaPago'),
                'rfc_src':  src.get('rfc'),
                'rfc_dst':  dst.get('rfc')
            })

            cfdi_ids += (str(cfdi.id),)

        if len(cfdi_ids):
            self.env.cr.execute(
                "UPDATE hr_xml_cfdi SET send_date = send_date + '6 hours'::interval, cert_date = cert_date + '6 hours'::interval WHERE id IN (%s)" % ','.join(cfdi_ids)
            )

        self.env.cr.commit()

        return {
            'type' : 'ir.actions.act_url',
            'url': '/hr_reports/cfdi_errors?export_type=%s' % self.export_type,
            'target': 'self' if self.export_type == 'X' else 'new',
        }