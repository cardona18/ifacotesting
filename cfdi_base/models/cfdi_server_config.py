# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class cfdi_server_config(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'cfdi.server.config'

    default_service_url = fields.Char(
        string='URL',
        required=True,
        help="URL de WebService (WSDL)",
        default_model='cfdi.server.config',
    )
    default_user = fields.Char(
        string='Usuario',
        required=True,
        help="Usuario de WebService",
        default_model='cfdi.server.config',
    )
    default_password = fields.Char(
        string='Contraseña',
        required=True,
        help="Contraseña de WebService",
        default_model='cfdi.server.config',
    )