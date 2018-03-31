# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorresgi18@gmail.com)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_work_period_tmp(models.TransientModel):
    _name = 'hr.work.period.tmp'
    _description = 'HR WORK PERIOD TMP'

    period_id = fields.Many2one(
        string='Periodo',
        comodel_name='hr.work.period'
    )
    employee_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee'
    )
    work_days = fields.Float(
        string='Días trabajados',
        default=0.0,
        digits=(16, 2)
    )
    extra_time = fields.Float(
        string='Horas extra',
        default=0.0,
        digits=(16, 2)
    )