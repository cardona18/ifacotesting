# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

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