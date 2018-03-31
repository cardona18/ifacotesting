# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_paysheet_sat_concept(models.Model):
    _name = 'hr.paysheet.sat.concept'
    _description = 'HR PAYSHEET SAT CONCEPT'

    name = fields.Char(
        string='Nombre',
        required=True
    )
    code = fields.Char(
        string='Clave',
        size=20
    )
    ctype = fields.Selection(
        string='Tipo',
        size=1,
        selection=[
            ('+', 'Percepción'),
            ('-', 'Deducción')
        ]
    )

    @api.multi
    def name_get(self):

        res = []

        for item in self:
            res.append((item.id, item.code + ' - ' + item.name))

        return res
