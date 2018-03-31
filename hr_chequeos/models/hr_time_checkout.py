# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_time_checkout(models.Model):
    _name = 'hr.time.checkout'
    _description = 'HR TIME CHECKOUT'

    name = fields.Char(
        string='Nombre'
    )
    employee_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee'
    )
    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company',
        related='employee_id.company_id'
    )
    check_time = fields.Datetime(
        string='Fecha y hora'
    )
    node_id = fields.Many2one(
        string='Nodo',
        comodel_name='hr.timecheck.node'
    )

    @api.model
    def create(self, vals):
        rec = super(hr_time_checkout, self).create(vals)

        rec.sudo().write({
            'name': 'TC-%s' % str(rec.id).zfill(4)
        })

        return rec