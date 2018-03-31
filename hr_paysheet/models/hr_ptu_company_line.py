# -*- coding: utf-8 -*-
# © <2017> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api

class hr_ptu_company_line(models.TransientModel):
    _name = 'hr.ptu.company.line'
    _description = 'HR PTU COMPANY LINE'

    wizard_id = fields.Many2one(
        string='Wizard',
        comodel_name='hr.ptu.wizard'
    )
    company_id = fields.Many2one(
        string='Empresa',
        comodel_name='res.company'
    )
    amount = fields.Float(
        string='Cantidad',
        digits=(16, 2)
    )
    employee_id = fields.Many2one(
        string='Empleado sindicalizado',
        comodel_name='hr.employee'
    )
    wage_sum = fields.Float(
        string='Suma de sueldos',
        default=0.0,
        digits=(16, 2)
    )
    wd_sum = fields.Float(
        string='Suma de días trabajados',
        default=0.0,
        digits=(16, 2)
    )
    wage_factor = fields.Float(
        string='Factor de sueldo',
        default=0.0,
        digits=(16, 18)
    )
    wd_factor = fields.Float(
        string='Factor de días trabajados',
        default=0.0,
        digits=(16, 18)
    )
    emp_line_ids = fields.One2many(
        string='Lineas de empleado',
        comodel_name='hr.ptu.line',
        inverse_name='company_line_id'
    )

    @api.onchange('company_id')
    def check_company_id(self):

        self.employee_id = False