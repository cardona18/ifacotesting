# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_employer_registration(models.Model):
    _name = 'hr.employer.registration'
    _description = 'HR EMPLOYER REGISTRATION'

    name = fields.Char(
        string='Registro',
        required=True
    )
    company_id = fields.Many2one(
        string='Compañia',
        comodel_name='res.company'
    )
    tax_percent = fields.Float(
        string='Porcentaje gravable',
        digits=(0, 4),
    )
    place = fields.Char(
        string='Ubicación'
    )
    guide = fields.Char(
        string='No. de guía',
        help='No. de guía para disco bimestral IMSS'
    )
    zip_code = fields.Char(
        string='Código postal',
        size=5
    )
    risk_id = fields.Many2one(
        string='Riesgo',
        comodel_name='hr.work.risk'
    )