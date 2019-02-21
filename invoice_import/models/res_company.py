# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class res_company(models.Model):
    _inherit = 'res.company'

    invoice_db = fields.Char(
        string='DB Facturas',
        size=20
    )
    import_server_id = fields.Many2one(
        string='Servidor',
        comodel_name='ir.conf.sqlserver'
    )
    smb_domain = fields.Char(
        string='Dominio'
    )
    smb_user = fields.Char(
        string='Usuario'
    )
    smb_pass = fields.Char(
        string='Contraseña'
    )
    smb_path = fields.Char(
        string='Ruta'
    )