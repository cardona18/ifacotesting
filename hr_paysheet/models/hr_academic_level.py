# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_academic_level(models.Model):
    _name = 'hr.academic.level'
    _description = 'HR ACADEMIC LEVEL'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    short_name = fields.Char(
        string='Abreviatura',
        size=20
    )
    old_id = fields.Integer(
        string='Clave'
    )
    antique_bonus = fields.Boolean(
        string='Bono de antigüedad'
    )