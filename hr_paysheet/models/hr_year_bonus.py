# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_year_bonus(models.Model):
    _name = 'hr.year.bonus'
    _description = 'HR YEAR BONUS'

    profession = fields.Boolean(
        string='Maestría / Doctorado'
    )
    years = fields.Integer(
        string='Años'
    )
    days = fields.Float(
        string='Días'
    )

