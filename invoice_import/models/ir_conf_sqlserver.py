# -*- coding: utf-8 -*-
# © <2017> < ()>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

class ir_conf_sqlserver(models.Model):
    _name = 'ir.conf.sqlserver'
    _description = 'IR CONF SQLSERVER'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    server_addr = fields.Char(
        string='Host',
        required=True,
        size=40
    )
    server_user = fields.Char(
        string='Usuario',
        required=True,
        size=80
    )
    server_pass = fields.Char(
        string='Contraseña',
        required=True,
        size=80
    )
    server_port = fields.Integer(
        string='Puerto',
        default=0,
        help='Puerto por defecto: 0'
    )