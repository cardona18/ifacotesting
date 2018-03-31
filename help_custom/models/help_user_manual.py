# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class help_user_manual(models.Model):
    _name = 'help.user.manual'
    _description = 'HELP USER MANUAL'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    manual = fields.Binary(
        string='Manual'
    )
    manual_filename = fields.Char(
        string='Archivo'
    )
