# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_sua_state(models.Model):
    _name = 'hr.sua.state'
    _description = 'HR SUA STATE'

    name = fields.Char(
        string='Nombre',
        size=30,
        required=True
    )
    code = fields.Integer(
        string='Code',
        required=True
    )
