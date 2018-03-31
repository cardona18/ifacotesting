# -*- coding: utf-8 -*-
# © <2016> <Omar Torres Silva (otorres@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class commentary_360(models.Model):
    _name = 'commentary.360'

    name = fields.Text(
        string='Nombre',
        required=True,
    )

    evalu_plan  = fields.Many2one(
        'hr.evaluation.360',
        string='Plan ejecutado',
        required=True,
    )

    id_excute_plan = fields.Integer(
        string='Numero de ejecución del plan',
        related='evalu_plan.id_excute_plan',
        ondelete="cascade",
        readonly=True
    )

    employee_evaluator  = fields.Many2one(
        comodel_name='hr.employee',
        string='Empleado evaluador',
        required=True,
        domain=['|',('active','=',True),('active','=',False)]
    )
