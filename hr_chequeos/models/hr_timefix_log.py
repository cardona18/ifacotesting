# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_timefix_log(models.Model):
    _name = 'hr.timefix.log'
    _description = 'HR TIMEFIX LOG'

    name = fields.Char(
        string='Nombre'
    )
    employee_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee'
    )
    log_detail = fields.Text(
        string='Detalle'
    )

    @api.model
    def create(self, vals):

        rec = super(hr_timefix_log, self).create(vals)

        rec.sudo().write({
            'name': 'LOG-%s' % str(rec.id).zfill(6)
        })

        return rec
