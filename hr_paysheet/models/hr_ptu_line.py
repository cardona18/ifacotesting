# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_ptu_line(models.TransientModel):
    _name = 'hr.ptu.line'
    _description = 'HR PTU LINE'

    wizard_id = fields.Many2one(
        string='Wizard',
        comodel_name='hr.ptu.wizard'
    )
    employee_id = fields.Many2one(
        string='Empleado',
        comodel_name='hr.employee'
    )
    wage = fields.Float(
        string='Salario anual',
        digits=(16, 2)
    )
    base_wage = fields.Float(
        string='Salario base',
        digits=(16, 2)
    )
    ptu_amount = fields.Float(
        string='Monto pagado',
        digits=(16, 2)
    )
    amount = fields.Float(
        string='Subtotal',
        digits=(16, 2)
    )
    worked_days = fields.Float(
        string='Días trabajados',
        digits=(16, 6)
    )
    ptu_days = fields.Integer(
        string='Días de PTU',
        default=0
    )
    daily_pantry = fields.Float(
        string='Despensa diaria',
        digits=(16, 2)
    )
    company_line_id = fields.Many2one(
        string='PTU por empresa',
        comodel_name='hr.ptu.company.line'
    )
    wage_ptu = fields.Float(
        string='P.T.U. por sueldo'
    )
    wd_ptu = fields.Float(
        string='P.T.U. días trabajados'
    )
    last_wage = fields.Float(
        string='Último salario',
        digits=(16, 2)
    )
    wage_limit = fields.Float(
        string='Salario limite',
        digits=(16, 2)
    )
    has_max_wage = fields.Boolean(
        string='Salario tope',
        default=False
    )
    month_wage = fields.Float(
        string='Sueldo mensual',
        digits=(16, 2)
    )