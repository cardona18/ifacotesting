# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_company_change(models.Model):
    _name = 'hr.company.change'
    _description = 'HR COMPANY CHANGE'

    name = fields.Char(
        string='Nombre'
    )
    employee_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee',
        ondelete='cascade'
    )
    last_company_id = fields.Many2one(
        string='Empresa anterior',
        comodel_name='res.company'
    )
    new_company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company'
    )

    @api.model
    def create(self, vals):
        rec = super(hr_company_change, self).create(vals)

        rec.sudo().write({
            'name': 'CC-%s' % str(rec.id).zfill(6)
        })

        return rec