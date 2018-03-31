# -*- coding: utf-8 -*-
# © <2016> <Juan Carlos Vazquez Beas (jcvazquez@grupoifaco.com.mx)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

class hr_states_eval(models.Model):
    _name = 'hr.states.eval'
    _description = 'HR STATES EVAL'

    state   = fields.Selection([('no_send', 'No enviado'),
                              ('no_requ', 'Enviada (En espera de respuestas)'),
                              ('no_email', '(Sin correo configurado)'),
                              ('yes_requ', 'Evaluación contestada'),
                                ], string='Estado', default='no_send')

    type_evaluators   = fields.Selection([('auto_eval', 'Autoevaluación'),
                              ('boss_eval', 'Jefe'),
                              ('collabo_eval', 'Subordinado'),
                              ('partner_eval', 'Compañero'),
                              ('client_eval', 'Cliente'),
                            ], string='Tipo de evaluador')

    evaluators_id   = fields.Many2one(
        comodel_name='hr.employee',
        string='Empleados evaluadores',
        domain=['|',('active','=',True),('active','=',False)]
    )

    num_resend = fields.Integer(
        'Cantidad de Reenvíos',
    )

    states_eval_id = fields.Many2one(
        string='Estados',
        comodel_name='hr.evaluation.360',
    )