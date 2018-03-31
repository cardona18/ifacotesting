# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from suds import WebFault
from suds.client import Client

from odoo import fields, models, api
from odoo.exceptions import UserError

class res_company(models.Model):
    _inherit = 'res.company'

    cert_file = fields.Binary(
        string='Certificado (.cer)'
    )
    cer_filename = fields.Char(
        string='Archivo (.cer)'
    )
    key_file = fields.Binary(
        string='Llave (.key)'
    )
    key_filename = fields.Char(
        string='Archivo (.key)'
    )
    cert_pass = fields.Char(
        string='Contraseña',
        password=True
    )
    regime_id = fields.Many2one(
        string='Regimen',
        comodel_name='cfdi.financial.regime'
    )
    rfc = fields.Char(
        string='RFC',
        size=50
    )
    cfdi_cancel = fields.Boolean(
        string='Cancelación CFDI'
    )

    @api.multi
    def cfdi_cancel_enable(self):

        server_config = self.env['cfdi.server.config'].create({})
        config = {
            'url': server_config['default_service_url']
        }
        ws_options = {
            'UserID': server_config['default_user'],
            'UserPass': server_config['default_password'],
            'emisorRFC': self.rfc
        }

        try:

            client = Client(config['url'], timeout=10)

            ws_options.update({
                'archivoCer': self.cert_file,
                'archivoKey': self.key_file,
                'clave': self.cert_pass
            })
            response = client.service.activarCancelacion(ws_options)
            result = True

        except WebFault, e:
            error_code = e.fault.faultcode
            error = e.fault.faultstring
            request = client.last_sent()
            result = False
        except Exception, e:
            error_code = 'LOST_CONNECTION'
            error = e.message
            result = False

        if not result:
            raise UserError('{0} - {1}'.format(error_code, error))

        self.cfdi_cancel = True