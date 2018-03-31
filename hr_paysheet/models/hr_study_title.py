# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_study_title(models.Model):
    _name = 'hr.study.title'
    _description = 'HR STUDY TITLE'

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