# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_leave(models.Model):
    _name = 'hr.leave'
    _description = 'HR LEAVE'

    name = fields.Char(
        string='Nombre'
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
    leave_type = fields.Selection(
        string='Tipo de baja',
        selection=[
            ('1', 'TÉRMINO DE CONTRATO'),
            ('2', 'SEPARACIÓN VOLUNTARIA'),
            ('3', 'ABANDONO DE EMPLEO'),
            ('4', 'DEFUNCIÓN'),
            ('5', 'CLAUSURA'),
            ('6', 'OTRAS'),
            ('7', 'AUSENTISMO'),
            ('8', 'RESCISIÓN DE CONTRATO'),
            ('9', 'JUBILACIÓN'),
            ('A', 'PENSIÓN')
        ]
    )
    move_date = fields.Date(
        string='Fecha'
    )

    @api.model
    def create(self, vals):
        rec = super(hr_leave, self).create(vals)

        rec.sudo().write({
            'name': '%s-%s' % (rec.employee_id.company_id.short_name, str(rec.employee_id.old_id).zfill(4))
        })

        return rec