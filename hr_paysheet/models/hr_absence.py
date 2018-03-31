# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_absence(models.Model):
    _name = 'hr.absence'
    _description = 'HR ABSENCE'

    name = fields.Char(
        string='Nombre'
    )
    old_id = fields.Integer(
        string='Clave'
    )
    employee_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee',
        required=True
    )
    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company',
        related='employee_id.company_id'
    )
    from_date = fields.Date(
        string='Desde'
    )
    to_date = fields.Date(
        string='Hasta'
    )

    @api.model
    def create(self, vals):
        rec = super(hr_absence, self).create(vals)

        rec.sudo().write({
            'name': '%s-%s' % (rec.employee_id.company_id.short_name, str(rec.employee_id.old_id).zfill(4))
        })

        return rec