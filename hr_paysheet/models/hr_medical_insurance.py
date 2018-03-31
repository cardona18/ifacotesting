# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_medical_insurance(models.Model):
    _name = 'hr.medical.insurance'
    _description = 'HR MEDICAL INSURANCE'

    name = fields.Char(
        string='Nombre'
    )
    from_date = fields.Date(
        string='Inicia'
    )
    to_date = fields.Date(
        string='Finaliza'
    )
    from_years = fields.Integer(
        string='Desde'
    )
    to_years = fields.Integer(
        string='Hasta'
    )
    male = fields.Float(
        string='Hombre'
    )
    female = fields.Float(
        string='Mujer'
    )