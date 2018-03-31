# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_holidays_line(models.Model):
    _name = 'hr.holidays.line'
    _description = 'HR HOLIDAYS LINE'

    name = fields.Char(
        string='Folio'
    )
    employee_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee'
    )
    year_num = fields.Integer(
        string='Aniversario'
    )
    from_date = fields.Date(
        string='Desde'
    )
    to_date = fields.Date(
        string='Hasta'
    )
    expires_at = fields.Date(
        string='Vencimiento'
    )
    expired_holidays = fields.Integer(
        string='Cantidad'
    )
    state = fields.Selection(
        string='Estado',
        default='draft',
        size=10,
        selection=[
            ('draft', 'Borrador'),
            ('ok', 'Aprobada')
        ]
    )

    @api.model
    def create(self, vals):
        rec = super(hr_holidays_line, self).create(vals)

        rec.sudo().write({
            'name': 'VV-%s' % str(rec.id).zfill(6)
        })

        return rec