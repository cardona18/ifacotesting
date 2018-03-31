# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class mail_domain_route(models.Model):
    _name = 'mail.domain.route'
    _description = 'MAIL DOMAIN ROUTE'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    domain_regex = fields.Char(
        string='Expresión'
    )
    server_id = fields.Many2one(
        string='Servidor',
        comodel_name='ir.mail_server'
    )
    sequence = fields.Integer(
        string='Prioridad'
    )

    _order = 'sequence'
