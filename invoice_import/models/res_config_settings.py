# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_import_invoice_db = fields.Char(
        string='Base de datos',
        related='company_id.invoice_db'
    )
    invoice_import_server_id = fields.Many2one(
        string='Servidor',
        related='company_id.import_server_id'
    )
    smb_domain = fields.Char(
        string='Dominio',
        related='company_id.smb_domain'
    )
    smb_user = fields.Char(
        string='Usuario',
        related='company_id.smb_user'
    )
    smb_pass = fields.Char(
        string='Contraseña',
        related='company_id.smb_pass'
    )
    smb_path = fields.Char(
        string='Ruta',
        related='company_id.smb_path'
    )