# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_salary_change(models.Model):
    _name = 'hr.salary.change'
    _description = 'HR SALARY CHANGE'

    name = fields.Char(
        string='Clave'
    )
    contract_id = fields.Many2one(
        string='Contrato',
        comodel_name='hr.contract',
        ondelete='cascade'
    )
    old_salary = fields.Float(
        string='Salario anterior'
    )
    old_sdi = fields.Float(
        string='SDI anterior'
    )
    new_salary = fields.Float(
        string='Salario nuevo'
    )
    new_sdi = fields.Float(
        string='SDI nuevo'
    )
    move_date = fields.Date(
        string='Fecha'
    )

    @api.model
    def create(self, vals):
        rec = super(hr_salary_change, self).create(vals)

        rec.sudo().write({
            'name': 'CS-%s' % str(rec.id).zfill(6)
        })

        return rec