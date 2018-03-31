# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_timecheck(models.Model):
    _name = 'hr.timecheck'
    _description = 'HR TIMECHECK'

    _sql_constraints = [
        ('unique_hr_timecheck', 'unique(workday_id, name)', 'El registro que intenta crear ya existe.')
    ]

    workday_id = fields.Many2one(
        string='Jornada',
        comodel_name='hr.timecheck.workday',
        ondelete='cascade'
    )
    name = fields.Selection(
        string='Número',
        required=True,
        size=1,
        selection=[
            ('1', 'Entrada 1'),
            ('2', 'Salida 1'),
            ('3', 'Entrada 2'),
            ('4', 'Salida 2'),
            ('5', 'Entrada 3'),
            ('6', 'Salida 3')
        ]
    )
    check_time = fields.Datetime(
        string='Fecha y hora',
        required=True
    )