# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_time_checker_config(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'hr.time.checker.config'

    default_ip_address = fields.Char(
        string='Dirección IP / Instancia',
        required=True,
        default_model='hr.time.checker.config',
    )
    default_database = fields.Char(
        string='Base de datos',
        required=True,
        default_model='hr.time.checker.config',
    )
    default_user = fields.Char(
        string='Usuario',
        required=True,
        help="Usuario de la instancia",
        default_model='hr.time.checker.config',
    )
    default_password = fields.Char(
        string='Contraseña',
        required=True,
        help="Contraseña de la instancia",
        default_model='hr.time.checker.config',
    )